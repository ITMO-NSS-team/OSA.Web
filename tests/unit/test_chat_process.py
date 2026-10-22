import os
import sys
import time
from unittest import TestCase

from osa_web.osa_tool.chat_process import ChatProcess

FAKE_CHAT = """
import json, sys
start = json.loads(sys.stdin.readline())
assert start['type'] == 'start'
question = {'type': 'question', 'id': 'q1', 'question': 'Approve?'}
question['fields'] = [{'name': 'accept', 'required': True}]
print(json.dumps(question), flush=True)
answer = json.loads(sys.stdin.readline())
assert answer == {'type': 'answer', 'id': 'q1', 'values': {'accept': 'yes'}}
completed = {'type': 'completed', 'summary': start['request']}
completed.update(tasks=[], artifacts=[], pull_request_url=None)
print(json.dumps(completed), flush=True)
"""


def collect_until(process: ChatProcess, event_type: str) -> list[dict]:
    events = []
    deadline = time.monotonic() + 4
    while time.monotonic() < deadline:
        events.extend(process.drain())
        if any(event["type"] == event_type for event in events):
            return events
        time.sleep(0.01)
    raise AssertionError(f"No {event_type} event: {events}")


class ChatProcessTests(TestCase):
    def test_two_sessions_keep_answers_and_results_separate(self) -> None:
        first = ChatProcess([sys.executable, "-u", "-c", FAKE_CHAT], {})
        second = ChatProcess([sys.executable, "-u", "-c", FAKE_CHAT], {})
        try:
            first.send({"type": "start", "repository": "https://example.com/a", "request": "first"})
            second.send(
                {"type": "start", "repository": "https://example.com/b", "request": "second"}
            )
            self.assertEqual(collect_until(first, "question")[0]["id"], "q1")
            self.assertEqual(collect_until(second, "question")[0]["id"], "q1")
            first.send({"type": "answer", "id": "q1", "values": {"accept": "yes"}})
            second.send({"type": "answer", "id": "q1", "values": {"accept": "yes"}})
            first_done = collect_until(first, "completed")
            second_done = collect_until(second, "completed")
            self.assertEqual(
                next(event["summary"] for event in first_done if event["type"] == "completed"),
                "first",
            )
            self.assertEqual(
                next(event["summary"] for event in second_done if event["type"] == "completed"),
                "second",
            )
        finally:
            first.cancel()
            second.cancel()

    def test_cancel_stops_process(self) -> None:
        process = ChatProcess([sys.executable, "-u", "-c", "import time; time.sleep(60)"], {})
        process.cancel()
        self.assertFalse(process.running)

    def test_cancel_stops_child_process(self) -> None:
        script = """
import json, subprocess, sys, time
child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])
print(json.dumps({'type': 'child', 'pid': child.pid}), flush=True)
time.sleep(60)
"""
        process = ChatProcess([sys.executable, "-u", "-c", script], {})
        child_pid = collect_until(process, "child")[0]["pid"]
        process.cancel()
        self.assertFalse(process.running)
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(child_pid, 0)
            except ProcessLookupError:
                break
            time.sleep(0.01)
        else:
            # An unreaped child can briefly remain as a zombie in the container.
            with open(f"/proc/{child_pid}/stat", encoding="utf-8") as file:
                self.assertEqual(file.read().split()[2], "Z")

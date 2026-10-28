"""Per-session subprocess transport for OSA's JSON-lines chat protocol."""

from __future__ import annotations

import json
import os
import queue
import signal
import subprocess
import threading
import weakref
from collections import deque
from typing import Any


def _terminate(process: subprocess.Popen[str]) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        # Windows has no process groups to signal, and os.killpg/SIGKILL do not
        # exist there; taskkill /T walks the child tree instead.
        subprocess.run(
            ["taskkill", "/F", "/T", "/PID", str(process.pid)],
            capture_output=True,
            check=False,
        )
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            pass
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait(timeout=3)


def _read_events(
    stream,
    events: queue.Queue[dict[str, Any]],
    console_output: deque[str],
    console_lock: threading.Lock,
) -> None:
    for line in stream:
        with console_lock:
            console_output.append(f"[stdout] {line.rstrip()[:4000]}")
        try:
            event = json.loads(line)
            if not isinstance(event, dict) or not isinstance(event.get("type"), str):
                raise TypeError("Expected an event object")
        except (json.JSONDecodeError, TypeError) as exc:
            event = {
                "type": "error",
                "message": f"Invalid OSA protocol output: {exc}",
                "recoverable": False,
            }
        events.put(event)


def _read_diagnostics(
    stream, lines: deque[str], console_output: deque[str], console_lock: threading.Lock
) -> None:
    for line in stream:
        diagnostic = line.rstrip()
        lines.append(diagnostic)
        with console_lock:
            console_output.append(f"[stderr] {diagnostic[:4000]}")


def _watch(
    process: subprocess.Popen[str],
    events: queue.Queue[dict[str, Any]],
    stdout_thread: threading.Thread,
    stderr_thread: threading.Thread,
    diagnostics: deque[str],
) -> None:
    exit_code = process.wait()
    stdout_thread.join(timeout=2)
    stderr_thread.join(timeout=2)
    for stream in (process.stdin, process.stdout, process.stderr):
        if stream is not None:
            stream.close()
    events.put(
        {
            "type": "process_exit",
            "exit_code": exit_code,
            "diagnostics": list(diagnostics)[-10:] if exit_code else [],
        }
    )


class ChatProcess:
    def __init__(self, command: list[str], env: dict[str, str]):
        self.process = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=env,
            start_new_session=True,
        )
        self.events: queue.Queue[dict[str, Any]] = queue.Queue()
        self.diagnostics: deque[str] = deque(maxlen=30)
        self.console_output: deque[str] = deque(maxlen=200)
        self._console_lock = threading.Lock()
        self._write_lock = threading.Lock()
        self._finalizer = weakref.finalize(self, _terminate, self.process)
        stdout_thread = threading.Thread(
            target=_read_events,
            args=(self.process.stdout, self.events, self.console_output, self._console_lock),
            daemon=True,
        )
        stderr_thread = threading.Thread(
            target=_read_diagnostics,
            args=(self.process.stderr, self.diagnostics, self.console_output, self._console_lock),
            daemon=True,
        )
        stdout_thread.start()
        stderr_thread.start()
        self._watcher = threading.Thread(
            target=_watch,
            args=(self.process, self.events, stdout_thread, stderr_thread, self.diagnostics),
            daemon=True,
        )
        self._watcher.start()

    def send(self, message: dict[str, Any]) -> None:
        with self._write_lock:
            if self.process.poll() is not None or self.process.stdin is None:
                raise RuntimeError("OSA chat has already stopped")
            self.process.stdin.write(json.dumps(message) + "\n")
            self.process.stdin.flush()

    def drain(self) -> list[dict[str, Any]]:
        events = []
        while True:
            try:
                events.append(self.events.get_nowait())
            except queue.Empty:
                return events

    @property
    def console_text(self) -> str:
        with self._console_lock:
            return "\n".join(self.console_output)

    def cancel(self) -> None:
        self._finalizer()
        self._watcher.join(timeout=3)

    @property
    def running(self) -> bool:
        return self.process.poll() is None

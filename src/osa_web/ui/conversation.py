"""Browser conversation for OSA's multi-agent pipeline."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

from osa_web.auth.state import get_display_name, is_guest_mode
from osa_web.logging_config import logger
from osa_web.osa_tool.chat_process import ChatProcess
from osa_web.osa_tool.command import build_chat_command
from osa_web.osa_tool.endpoint import check_endpoint
from osa_web.osa_tool.environment import build_osa_environment
from osa_web.osa_tool.models import OsaChatRequest
from osa_web.settings import get_runtime_path
from osa_web.state import keys
from osa_web.ui.attachment import render_attachment_block
from osa_web.ui.console_output import render_console_output
from osa_web.ui.publishing_confirmation import render_publishing_confirmation


def _reset_conversation() -> None:
    process = st.session_state.get(keys.CHAT_PROCESS)
    if process is not None:
        process.cancel()
    st.session_state[keys.CHAT_PROCESS] = None
    st.session_state[keys.CHAT_MESSAGES] = []
    st.session_state[keys.CHAT_PROGRESS] = []
    st.session_state[keys.CHAT_QUESTION] = None
    st.session_state[keys.CHAT_PENDING] = None
    st.session_state[keys.CHAT_TERMINAL] = False
    st.session_state[keys.CHAT_SHOW_CONSOLE] = False
    st.session_state[keys.CHAT_RUN_LLM] = None
    st.session_state.pop(keys.CHAT_STARTED_AT, None)
    st.session_state.pop(keys.CHAT_ATTACHMENT, None)
    st.session_state.pop("chat_attachment_selection_pills", None)
    st.session_state.pop(f"{keys.CHAT_ATTACHMENT}-dialog-source", None)
    st.session_state.pop("agentic-repository", None)


def _is_github_repository_url(value: str) -> bool:
    try:
        parsed = urlparse(value.strip())
        valid_host = parsed.hostname in {"github.com", "www.github.com"}
        has_authority_suffix = bool(parsed.username or parsed.password or parsed.port)
    except ValueError:
        return False
    if parsed.scheme != "https" or not valid_host or has_authority_suffix:
        return False
    if parsed.query or parsed.fragment:
        return False
    return len([part for part in parsed.path.split("/") if part]) == 2


def _publishing_enabled() -> bool:
    git = st.session_state[keys.CONFIGURATION]["agentic"]["git"]
    return not git["no-fork"] or not git["no-pull-request"]


def _start_run() -> None:
    pending = st.session_state[keys.CHAT_PENDING]
    config = st.session_state[keys.CONFIGURATION]
    check_endpoint(config["agentic"]["llm"])
    command = build_chat_command(
        OsaChatRequest(
            output_dir=pending["output_dir"],
            log_dir=str(get_runtime_path("log").parent),
            author=get_display_name(),
            configuration=config,
        )
    )
    env = build_osa_environment(
        guest=is_guest_mode(),
        api_key=st.session_state.get(keys.CONFIGURATION_AGENTIC_API_KEY),
        git_token=st.session_state.get(keys.GIT_TOKEN),
    )

    process = ChatProcess(command, env)
    try:
        process.send(
            {
                "type": "start",
                "repository": pending["repository"],
                "request": pending["request"],
                "attachment": pending["attachment"],
            }
        )
    except Exception:
        process.cancel()
        raise
    st.session_state[keys.CHAT_PROCESS] = process
    st.session_state[keys.CHAT_STARTED_AT] = datetime.now(UTC)
    st.session_state[keys.CHAT_RUN_LLM] = config["agentic"]["llm"].copy()
    st.session_state[keys.CHAT_MESSAGES].append({"role": "user", "content": pending["request"]})
    st.session_state[keys.CHAT_PENDING] = None
    st.session_state[keys.CHAT_TERMINAL] = False


def _record_start_failure(exc: Exception) -> None:
    logger.exception("Could not start OSA chat")
    st.session_state[keys.CHAT_MESSAGES].append(
        {
            "role": "assistant",
            "type": "error",
            "event": {"message": f"Could not start OSA chat: {exc}"},
        }
    )
    st.session_state[keys.CHAT_PENDING] = None


def _discard_pending_run() -> None:
    st.session_state[keys.CHAT_PENDING] = None


@st.dialog("Run OSA Tool", on_dismiss=_discard_pending_run)
def confirm_agentic_run() -> None:
    pending = st.session_state[keys.CHAT_PENDING]
    cancelled, confirmed = render_publishing_confirmation(pending["repository"])
    if cancelled:
        _discard_pending_run()
        st.rerun()
    if confirmed:
        try:
            _start_run()
        except (OSError, RuntimeError, ValueError) as exc:
            _record_start_failure(exc)
        st.rerun()


def _stage_run(request: str, repository: str) -> None:
    if is_guest_mode() and st.session_state[keys.CONFIGURATION]["agentic"]["llm"]["api"] in {
        "itmo",
        "host",
    }:
        st.error("Select OpenAI or Ollama in Agentic configuration before running as a guest.")
        return
    if not _is_github_repository_url(repository):
        st.error("Enter a GitHub repository URL such as https://github.com/owner/repo.")
        return
    if not request.strip():
        st.error("Describe what you want OSA to do.")
        return
    selected_attachment = st.session_state.get(keys.CHAT_ATTACHMENT)
    attachment = selected_attachment["data"] if selected_attachment else None
    if selected_attachment and selected_attachment["type"] == "URL":
        parsed_attachment = urlparse(attachment)
        if parsed_attachment.scheme not in {"http", "https"} or not parsed_attachment.netloc:
            st.error("Attachment URL must start with http:// or https://.")
            return
    elif selected_attachment and selected_attachment["type"] == "File":
        path = Path(attachment).resolve()
        tmp_root = Path(st.session_state[keys.TMPDIR]).resolve()
        if not path.is_file() or not path.is_relative_to(tmp_root):
            st.error("The uploaded attachment is no longer available.")
            return

    output_dir = Path(tempfile.mkdtemp(prefix="chat-", dir=st.session_state[keys.TMPDIR]))

    st.session_state[keys.CHAT_PENDING] = {
        "repository": repository.strip(),
        "request": request.strip(),
        "attachment": attachment,
        "output_dir": str(output_dir),
    }
    if not _publishing_enabled():
        try:
            _start_run()
        except (OSError, RuntimeError, ValueError) as exc:
            _record_start_failure(exc)


def _record_event(event: dict) -> None:
    kind = event["type"]
    if kind == "progress":
        progress = st.session_state[keys.CHAT_PROGRESS]
        item = f"{event.get('agent', 'Agent')}: {event.get('status', 'working')}"
        if not progress or progress[-1] != item:
            progress.append(item)
        return
    if kind == "started":
        return
    if kind == "question":
        st.session_state[keys.CHAT_QUESTION] = event
        st.session_state[keys.CHAT_MESSAGES].append(
            {
                "role": "assistant",
                "content": event.get("question", "Additional information required"),
            }
        )
        return
    if kind == "review":
        st.session_state[keys.CHAT_MESSAGES].append(
            {"role": "assistant", "type": "review", "event": event}
        )
        return
    if kind in {"completed", "stopped"}:
        st.session_state[keys.CHAT_TERMINAL] = True
        st.session_state[keys.CHAT_QUESTION] = None
        st.session_state[keys.CHAT_MESSAGES].append(
            {"role": "assistant", "type": kind, "event": event}
        )
        return
    if kind == "error":
        if event.get("recoverable"):
            detail = event.get("message", "Invalid answer")
            st.session_state[keys.CHAT_MESSAGES].append(
                {
                    "role": "assistant",
                    "content": f"Please correct the answer: {detail}",
                }
            )
        else:
            st.session_state[keys.CHAT_TERMINAL] = True
            st.session_state[keys.CHAT_QUESTION] = None
            st.session_state[keys.CHAT_SHOW_CONSOLE] = True
            st.session_state[keys.CHAT_MESSAGES].append(
                {"role": "assistant", "type": "error", "event": event}
            )
        return
    if kind == "process_exit" and st.session_state[keys.CHAT_TERMINAL]:
        if event.get("exit_code"):
            for message in reversed(st.session_state[keys.CHAT_MESSAGES]):
                if message.get("type") == "error":
                    message["event"]["diagnostics"] = event.get("diagnostics") or []
                    break
        return
    if kind == "process_exit":
        exit_code = event.get("exit_code")
        st.session_state[keys.CHAT_TERMINAL] = True
        st.session_state[keys.CHAT_QUESTION] = None
        st.session_state[keys.CHAT_SHOW_CONSOLE] = True
        st.session_state[keys.CHAT_MESSAGES].append(
            {
                "role": "assistant",
                "type": "error",
                "event": {
                    "message": f"OSA stopped before completing (exit code {exit_code}).",
                    "diagnostics": event.get("diagnostics") or [],
                },
            }
        )


def _render_artifacts(paths: list[str], scope: str = "") -> None:
    output_root = Path(st.session_state[keys.TMPDIR]).resolve()
    # The same artifact is listed again by every later review, so the key has to
    # carry the message it belongs to, or Streamlit rejects the duplicate.
    seen: set[Path] = set()
    for value in paths[:30]:
        path = Path(value).resolve()
        if not path.is_file() or not path.is_relative_to(output_root) or path in seen:
            continue
        seen.add(path)
        with path.open("rb") as file:
            st.download_button(
                f"Download {path.name}",
                data=file,
                file_name=path.name,
                key=f"chat-artifact-{scope}-{path}",
                width="stretch",
            )


def _render_tasks(tasks: list[dict]) -> None:
    if tasks:
        st.caption("Tasks: " + ", ".join(f"{task['id']} ({task['status']})" for task in tasks))
    for task in tasks:
        if task.get("result") is not None:
            with st.expander(f"{task['id']} result"):
                st.write(task["result"])


def _render_messages() -> None:
    for index, message in enumerate(st.session_state[keys.CHAT_MESSAGES]):
        with st.chat_message(message["role"]):
            kind = message.get("type")
            if kind == "completed":
                event = message["event"]
                st.markdown(event.get("summary") or "Run completed.")
                _render_tasks(event.get("tasks") or [])
                if event.get("pull_request_url"):
                    st.link_button("Open pull request", event["pull_request_url"])
                _render_artifacts(event.get("artifacts") or [], scope=str(index))
            elif kind == "review":
                event = message["event"]
                st.markdown("Review the latest agent results before approving.")
                _render_tasks(event.get("tasks") or [])
                for item in event.get("events") or []:
                    st.markdown(f"- {item['kind']}: `{item['target']}`")
                _render_artifacts(event.get("artifacts") or [], scope=str(index))
            elif kind == "stopped":
                st.warning(message["event"].get("message", "Run stopped."))
            elif kind == "error":
                st.error(message["event"].get("message", "OSA failed."))
                diagnostics = message["event"].get("diagnostics") or []
                if diagnostics:
                    st.caption("Recent OSA diagnostics")
                    st.code("\n".join(diagnostics), language="text")
            else:
                st.markdown(message["content"])


def _render_question(question: dict, process: ChatProcess) -> None:
    with st.form(f"chat-question-{question['id']}"):
        values: dict[str, str | None] = {}
        for field in question.get("fields", []):
            name = field["name"]
            label = field.get("prompt", name)
            if name == "accept":
                values[name] = st.selectbox(
                    label,
                    ["Yes", "No"],
                    index=None,
                    placeholder="Choose yes or no",
                    key=f"chat-answer-{question['id']}-{name}",
                    help="Approve the result or request changes. Default: no selection.",
                )
            else:
                values[name] = st.text_input(
                    label,
                    key=f"chat-answer-{question['id']}-{name}",
                    help=(
                        "Required answer. Default: empty."
                        if field.get("required")
                        else "Optional answer. Default: empty."
                    ),
                )
        submitted = st.form_submit_button(
            "Send answer", width="stretch", help="Send these answers to the waiting agent."
        )
    if submitted:
        if any(
            field.get("required") and not values.get(field["name"]) for field in question["fields"]
        ):
            st.error("Fill in every required answer.")
            return
        answers = {key: value.strip() if value else None for key, value in values.items()}
        if answers.get("accept"):
            answers["accept"] = answers["accept"].lower()
        try:
            process.send({"type": "answer", "id": question["id"], "values": answers})
        except (OSError, RuntimeError) as exc:
            st.error(f"Could not send answer: {exc}")
            return
        st.session_state[keys.CHAT_MESSAGES].append(
            {
                "role": "user",
                "content": ", ".join(f"{key}: {value}" for key, value in answers.items() if value),
            }
        )
        st.session_state[keys.CHAT_QUESTION] = None
        st.rerun(scope="fragment")


@st.fragment(run_every="1s")
def _conversation_panel() -> None:
    process: ChatProcess | None = st.session_state[keys.CHAT_PROCESS]
    if process is not None:
        for event in process.drain():
            _record_event(event)

    pending = st.session_state[keys.CHAT_PENDING]
    messages = st.session_state[keys.CHAT_MESSAGES]
    terminal = st.session_state[keys.CHAT_TERMINAL]
    has_session = process is not None or pending is not None or terminal or bool(messages)
    outcome = next(
        (
            message.get("type")
            for message in reversed(messages)
            if message.get("type") in {"completed", "stopped", "error"}
        ),
        None,
    )

    if has_session:
        controls_left, controls_right = st.columns([0.8, 0.2], gap="medium")
        with controls_left:
            if process is not None and process.running and not terminal:
                if st.button(
                    "Cancel run",
                    key="chat-cancel-run",
                    icon=":material/stop_circle:",
                    help="Stop OSA and its child processes. Default: let the run continue.",
                ):
                    process.cancel()
                    _record_event(
                        {"type": "stopped", "reason": "cancelled", "message": "Run cancelled."}
                    )
                    st.rerun(scope="fragment")
            elif outcome == "completed":
                st.success("Run completed successfully.", icon=":material/check_circle:")
        with controls_right:
            if st.button(
                "New run",
                key="chat-new-run",
                icon=":material/add_circle_outline:",
                width="stretch",
                help="End and clear this run, including a running process.",
            ):
                _reset_conversation()
                st.rerun()

    chat_column, steps_column = st.columns([0.8, 0.2], gap="medium")
    with chat_column:
        _render_messages()
        question = st.session_state[keys.CHAT_QUESTION]
        if question and process:
            _render_question(question, process)
        elif process is None and pending is None and not terminal:
            st.caption("Request: describe the repository work for the agents.")
            submission = st.chat_input(
                "Describe what OSA should do",
                key="agentic-request",
            )
            if submission:
                _stage_run(submission, st.session_state.get("agentic-repository", ""))
                st.rerun()

    with steps_column:
        progress = st.session_state[keys.CHAT_PROGRESS]
        if process is not None or progress:
            working = process is not None and process.running and not terminal
            with st.status(
                "Agentic steps",
                state="running"
                if working
                else "error"
                if outcome in {"error", "stopped"}
                else "complete",
                type="compact",
                # This fragment reruns every second, which rebuilds the status block and
                # discards any manual expansion; keep the agent steps open instead.
                expanded=True,
            ):
                if progress:
                    for item in progress[-20:]:
                        st.caption(item)
                elif working:
                    st.caption("Waiting for agent activity...")

    if process is not None:
        llm = st.session_state[keys.CHAT_RUN_LLM] or {}
        provider = f"Provider: {llm.get('api', 'unknown')} · Model: {llm.get('model', 'unknown')}"
        if llm.get("api") != "itmo":
            base_url = urlparse(llm.get("base-url") or "")
            provider += f" · Base URL: {base_url._replace(query='', fragment='').geturl()}"
        render_console_output(
            process.console_text,
            st.session_state.get("agentic-repository", ""),
            started_at=st.session_state.get(keys.CHAT_STARTED_AT),
            caption=provider,
            expanded=st.session_state[keys.CHAT_SHOW_CONSOLE],
        )


def render_conversation_tab() -> None:
    process = st.session_state[keys.CHAT_PROCESS]
    active = process is not None or st.session_state[keys.CHAT_PENDING] is not None
    st.container(height=5, border=False)
    st.markdown(
        '<h3 style="text-align: center;">To start an agentic conversation, please enter a GitHub repository URL and describe what you want OSA to do:</h3>',
        unsafe_allow_html=True,
    )
    st.container(height=5, border=False)
    with st.container(border=True):
        st.text_input(
            "Repository URL :red[*]",
            key="agentic-repository",
            placeholder="https://github.com/aimclub/OSA",
            disabled=active,
            persist_state="session",
            help="GitHub repository URL, such as https://github.com/aimclub/OSA. Required; default: empty.",
        )
        render_attachment_block(keys.CHAT_ATTACHMENT, disabled=active, full_width_buttons=True)
    if st.session_state[keys.CHAT_PENDING] is not None:
        confirm_agentic_run()
    _conversation_panel()

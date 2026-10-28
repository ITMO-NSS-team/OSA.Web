import asyncio
from datetime import UTC, datetime

import streamlit as st

from osa_web.auth.state import get_display_name, is_guest_mode
from osa_web.logging_config import logger
from osa_web.osa_tool.command import build_osa_command
from osa_web.osa_tool.endpoint import check_endpoint
from osa_web.osa_tool.environment import build_osa_environment
from osa_web.osa_tool.models import OsaRunRequest, ParsedOsaOutput
from osa_web.osa_tool.output_parser import parse_output_line, result_message
from osa_web.state import keys
from osa_web.state.session import reset_run_output
from osa_web.ui.console_output import render_console_output


async def run_osa_tool(output_container) -> None:
    """Run the osa-tools application."""
    try:
        reset_run_output()
        st.session_state[keys.RUN_STARTED_AT] = datetime.now(UTC)

        env = build_osa_environment(
            guest=is_guest_mode(),
            api_key=st.session_state.get(keys.CONFIGURATION_API_KEY),
            git_token=st.session_state.get(keys.GIT_TOKEN),
        )

        attachment = None
        if keys.ATTACHMENT in st.session_state:
            attachment = st.session_state[keys.ATTACHMENT].get("data")

        cmd = build_osa_command(
            OsaRunRequest(
                repo_url=st.session_state[keys.REPO_URL],
                mode=st.session_state[keys.MODE_SELECT],
                output_dir=st.session_state[keys.TMPDIR],
                author=get_display_name(),
                configuration=st.session_state[keys.CONFIGURATION],
                attachment=attachment,
            )
        )

        await asyncio.to_thread(
            check_endpoint,
            st.session_state[keys.CONFIGURATION][st.session_state[keys.MODE_SELECT]]["llm"],
        )

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )
        stderr_task = asyncio.create_task(process.stderr.read())

        cmd_log_msg = f"Running osa-tool with parameters: {cmd}"

        logger.info(cmd_log_msg)
        st.session_state[keys.OUTPUT_LOGS] = cmd_log_msg + "\n"
        last_line = None
        parsed = ParsedOsaOutput()

        while True:
            stdout_line = await process.stdout.readline()
            if not stdout_line:
                break

            if line := stdout_line.decode().strip():
                last_line = line
                previous_report_count = len(parsed.report_paths)
                previous_pr_link = parsed.pr_link
                parse_output_line(line, parsed)

                if len(parsed.report_paths) > previous_report_count:
                    report_path = parsed.report_paths[-1]
                    logger.info(f"Created PDF report: {report_path} ")
                    st.session_state[keys.OUTPUT_REPORT_PATHS].append(report_path)
                    st.session_state[keys.OUTPUT_REPORT_FILENAMES].append(
                        parsed.report_filenames[-1]
                    )

                if parsed.about_section:
                    st.session_state[keys.OUTPUT_ABOUT_SECTION] = parsed.about_section

                if parsed.pr_link and parsed.pr_link != previous_pr_link:
                    logger.info(f"Created Pull Request: {parsed.pr_link}")

                logger.debug(line)

                st.session_state[keys.OUTPUT_LOGS] += line + "\n"
                with output_container:
                    render_console_output(
                        st.session_state[keys.OUTPUT_LOGS],
                        st.session_state[keys.REPO_URL],
                        started_at=st.session_state[keys.RUN_STARTED_AT],
                        downloadable=False,
                    )

        st.session_state[keys.OUTPUT_EXIT_CODE] = await process.wait()
        stderr_output = (await stderr_task).decode(errors="replace").strip()
        if stderr_output:
            st.session_state[keys.OUTPUT_LOGS] += f"[stderr]\n{stderr_output}\n"
            for line in stderr_output.splitlines():
                parse_output_line(line, parsed)
        st.session_state[keys.OUTPUT_HAS_ERRORS] = bool(parsed.error_lines)
        st.session_state[keys.OUTPUT_HAS_WARNINGS] = bool(parsed.nonfatal_errors)
        st.session_state[keys.OUTPUT_MESSAGE] = result_message(
            st.session_state[keys.OUTPUT_EXIT_CODE], parsed, last_line
        )
        if st.session_state[keys.OUTPUT_EXIT_CODE] or parsed.error_lines:
            logger.error(
                "OSA tool reported failure (exit code %s, %s error lines). Last output: %s",
                st.session_state[keys.OUTPUT_EXIT_CODE],
                len(parsed.error_lines),
                last_line,
            )
    except Exception as e:  # noqa: BLE001 - Surface any launch failure in the UI.
        st.session_state[keys.OUTPUT_EXIT_CODE] = 1
        st.session_state[keys.OUTPUT_HAS_ERRORS] = True
        st.session_state[keys.OUTPUT_HAS_WARNINGS] = False
        st.session_state[keys.OUTPUT_MESSAGE] = f"Error executing OSA tool: {e!s}"
        st.session_state.setdefault(keys.OUTPUT_LOGS, "")
        logger.error(f"OSA tool execution failed: {e!s}", exc_info=True)
    finally:
        st.session_state[keys.RUNNING] = False
        st.rerun()

import asyncio
import os

import streamlit as st

from osa_web.auth.state import get_display_name
from osa_web.logging_config import logger
from osa_web.osa_tool.command import build_osa_command
from osa_web.osa_tool.models import OsaRunRequest, ParsedOsaOutput
from osa_web.osa_tool.output_parser import parse_output_line
from osa_web.state import keys
from osa_web.state.session import reset_run_output


async def run_osa_tool(output_container) -> None:
    """Run the osa-tools application."""
    try:
        reset_run_output()

        env = os.environ.copy()
        env.update({"COLUMNS": "200", "TERM": "xterm-256color", "PYTHONUNBUFFERED": "1"})
        if keys.CONFIGURATION_API_KEY in st.session_state:
            env.update({"OPENAI_API_KEY": st.session_state[keys.CONFIGURATION_API_KEY]})

        if st.session_state[keys.GIT_TOKEN]:
            env["GIT_TOKEN"] = st.session_state[keys.GIT_TOKEN]

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

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

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
                output_container.expander("See Console Output", icon=":material/terminal:").code(
                    st.session_state[keys.OUTPUT_LOGS],
                    height=350,
                )

        st.session_state[keys.OUTPUT_EXIT_CODE] = await process.wait()
        if st.session_state[keys.OUTPUT_EXIT_CODE] == 0:
            st.session_state[keys.OUTPUT_MESSAGE] = (
                f'Everything is alright! {f"**Pull Request created**: {parsed.pr_link}" if parsed.pr_link else ""}'
            )
        else:
            stderr_output = await process.stderr.read()
            error_message = stderr_output.decode().strip()
            st.session_state[keys.OUTPUT_MESSAGE] = f"**Error running OSA tool**: `{last_line}`"
            logger.error(
                "OSA tool execution failed with code %s: %s\n%s",
                st.session_state[keys.OUTPUT_EXIT_CODE],
                last_line,
                error_message,
            )
    except Exception as e:
        st.error(f"Error executing OSA tool: {e!s}")
        logger.error(f"OSA tool execution failed: {e!s}", exc_info=True)
    finally:
        st.session_state[keys.RUNNING] = False
        st.rerun()

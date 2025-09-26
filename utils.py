import asyncio
import numbers
import os
import re

import streamlit as st

from logger_config import logger


def _transform_configuration_to_cmd(cmd: list, configuration: dict):
    """ """
    for k, v in configuration.items():
        if isinstance(v, bool) and v:
            cmd.extend((f"--{k}",))
        elif isinstance(v, str) and v != "":
            cmd.extend((f"--{k}", v))
        elif isinstance(v, numbers.Number) and not isinstance(v, bool):
            cmd.extend((f"--{k}", str(v)))
        elif isinstance(v, list) and v:
            cmd.extend((f"--{k}", ", ".join([str(i) for i in v])))


async def run_osa_tool(output_container) -> None:
    """Run the osa-tools application."""
    try:
        # Clear streamlit state
        if "output_report_path" in st.session_state:
            del st.session_state["output_report_path"]
        if "output_report_filename" in st.session_state:
            del st.session_state["output_report_filename"]
        if "output_about_section" in st.session_state:
            del st.session_state["output_about_section"]

        # Создаем копию текущих переменных окружения
        env = os.environ.copy()
        # NOTE: Force Unbuffered Output & Adjust Terminal Width
        env.update(
            {"COLUMNS": "200", "TERM": "xterm-256color", "PYTHONUNBUFFERED": "1"}
        )
        if "configuration-api-key" in st.session_state:
            env.update({"OPENAI_API_KEY": st.session_state["configuration-api-key"]})

        # Убедимся, что GIT_TOKEN передается в процесс
        if st.session_state.git_token:
            env["GIT_TOKEN"] = st.session_state.git_token

        cmd = [
            "osa-tool",
            "-r",
            st.session_state.repo_url,
            "-m",
            st.session_state.mode_select,
            "-o",
            st.session_state.tmpdirname,
            "--web-mode",
            "--delete-dir",
        ]

        if "article" in st.session_state:
            cmd.extend(("--article", st.session_state.article.get("data")))

        _transform_configuration_to_cmd(cmd, st.session_state.configuration["git"])

        if st.session_state.mode_select == "advanced":
            _transform_configuration_to_cmd(
                cmd, st.session_state.configuration["general"]
            )
            _transform_configuration_to_cmd(cmd, st.session_state.configuration["llm"])
            if st.session_state.configuration["workflows"]["generate-workflows"]:
                _transform_configuration_to_cmd(
                    cmd, st.session_state.configuration["workflows"]
                )

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=env,
        )

        logger.info(f"Running osa-tool with parameters: {cmd}")
        st.session_state.output_logs = ""
        last_line = None
        pr_link = None

        while True:
            stdout_line = await process.stdout.readline()
            if not stdout_line:
                break

            if line := stdout_line.decode().strip():
                last_line = line
                if match := re.search(
                    r"PDF report successfully created in (\/.*.pdf)", line
                ):
                    logger.info(f"Created PDF report: {match.group(1)} ")
                    st.session_state.output_report_path = match.group(1)
                    st.session_state.output_report_filename = match.group(1).split("/")[
                        -1
                    ]
                if match := re.search(
                    r"(.*You can add the following.*|.*- Description:.*|.*- Homepage:.*|.*- Topics:.*|.*Please review and add them to your repository.*)",
                    line,
                ):
                    if "output_about_section" not in st.session_state:
                        st.session_state.output_about_section = ""
                    st.session_state.output_about_section += line + "\n\n"
                if match := re.search(
                    r".*pull request created successfully: (\S*)", line
                ):
                    logger.info(f"Created Pull Request: {match.group(1)}")
                    pr_link = match.group(1)

                logger.debug(line)

                st.session_state.output_logs += line + "\n"
                # TODO: developer only
                output_container.expander(
                    "See Console Output", icon=":material/terminal:"
                ).code(
                    st.session_state.output_logs,
                    height=350,
                )

        st.session_state.output_exit_code = await process.wait()
        if st.session_state.output_exit_code == 0:
            st.session_state.output_message = f'Everything is alright! {f"**Pull Request created**: {pr_link}" if pr_link else ""}'
        else:
            stderr_output = await process.stderr.read()
            error_message = stderr_output.decode().strip()
            st.session_state.output_message = (
                f"**Error running OSA tool**: `{last_line}`"
            )
            logger.error(
                f"OSA tool execution failed with code {st.session_state.output_exit_code}: {last_line}"
            )
    except Exception as e:
        st.error(f"Error executing OSA tool: {e!s}")
        logger.error(f"OSA tool execution failed: {e!s}", exc_info=True)
    finally:
        st.session_state.running = False
        st.rerun()

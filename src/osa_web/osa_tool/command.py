from __future__ import annotations

import numbers
import shlex
import sys
from typing import Any

from osa_web.osa_tool.models import OsaChatRequest, OsaRunRequest

LIST_OPTIONS = {
    "translate-readme",
    "convert-notebooks",
    "target-files",
    "python-versions",
    "branches",
}


def transform_configuration_to_cmd(cmd: list[str], configuration: dict[str, Any]) -> None:
    for key, value in configuration.items():
        if isinstance(value, bool) and value:
            cmd.append(f"--{key}")
        elif isinstance(value, str) and value != "":
            if key in LIST_OPTIONS:
                items = shlex.split(value)
                if items:
                    cmd.extend((f"--{key}", *items))
            else:
                cmd.extend((f"--{key}", value))
        elif isinstance(value, numbers.Number) and not isinstance(value, bool):
            cmd.extend((f"--{key}", str(value)))
        elif isinstance(value, list) and value:
            cmd.extend((f"--{key}", *(str(item) for item in value)))


def build_osa_command(request: OsaRunRequest) -> list[str]:
    mode_config = request.configuration[request.mode]
    cmd = [
        "osa-tool",
        "-r",
        request.repo_url,
        "-m",
        "basic" if request.mode == "basic" else "advanced",
        "-o",
        request.output_dir,
        "--author",
        request.author,
        "--web-mode",
    ]

    if request.attachment:
        cmd.extend(("--attachment", request.attachment))

    transform_configuration_to_cmd(cmd, mode_config["git"])
    general = mode_config["general"]
    transform_configuration_to_cmd(
        cmd,
        {
            key: value
            for key, value in general.items()
            if key not in {"notebook-report", "notebook-report-paths"}
        },
    )
    if general.get("notebook-report"):
        cmd.append("--notebook-report")
        cmd.extend(shlex.split(general.get("notebook-report-paths", "")))
    transform_configuration_to_cmd(cmd, mode_config["llm"])

    workflows = mode_config["workflows"]
    if workflows["generate-workflows"]:
        transform_configuration_to_cmd(cmd, workflows)

    return cmd


def build_chat_command(request: OsaChatRequest) -> list[str]:
    cmd = [
        sys.executable,
        "-m",
        "osa_tool.run_chat",
        "--web-chat",
        "--web-mode",
        "--output",
        request.output_dir,
        "--log-dir",
        request.log_dir,
        "--author",
        request.author,
    ]
    agentic = request.configuration["agentic"]
    transform_configuration_to_cmd(cmd, agentic["git"])
    transform_configuration_to_cmd(cmd, agentic["llm"])
    return cmd

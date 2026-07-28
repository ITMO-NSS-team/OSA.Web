from __future__ import annotations

import numbers
from typing import Any

from osa_web.osa_tool.models import OsaRunRequest


def transform_configuration_to_cmd(cmd: list[str], configuration: dict[str, Any]) -> None:
    for key, value in configuration.items():
        if isinstance(value, bool) and value:
            cmd.append(f"--{key}")
        elif isinstance(value, str) and value != "":
            cli_value = "openai" if value == "itmo" else value
            cmd.extend((f"--{key}", cli_value))
        elif isinstance(value, numbers.Number) and not isinstance(value, bool):
            cmd.extend((f"--{key}", str(value)))
        elif isinstance(value, list) and value:
            cmd.extend((f"--{key}", ", ".join([str(item) for item in value])))


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
    transform_configuration_to_cmd(cmd, mode_config["general"])
    transform_configuration_to_cmd(cmd, mode_config["llm"])

    workflows = mode_config["workflows"]
    if workflows["generate-workflows"]:
        transform_configuration_to_cmd(cmd, workflows)

    return cmd

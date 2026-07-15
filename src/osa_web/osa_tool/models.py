from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OsaRunRequest:
    repo_url: str
    mode: str
    output_dir: str
    author: str
    configuration: dict[str, Any]
    attachment: str | None = None


@dataclass
class ParsedOsaOutput:
    report_paths: list[str] = field(default_factory=list)
    report_filenames: list[str] = field(default_factory=list)
    about_section: str = ""
    pr_link: str | None = None


@dataclass(frozen=True)
class OsaRunResult:
    exit_code: int
    message: str
    parsed_output: ParsedOsaOutput

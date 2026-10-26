"""Load the public, curated examples shown in the Past runs tab."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import date
from importlib.resources import files
from pathlib import Path
from urllib.parse import urlsplit

from osa_web.state import keys

OUTCOMES = {"completed", "failed", "stopped"}
REQUIRED_FIELDS = {
    "id",
    "repository_url",
    "work_mode",
    "completed_at",
    "outcome",
    "summary",
    "steps",
}
OPTIONAL_FIELDS = {"pull_request_url"}
GITHUB_OWNER = re.compile(r"[A-Za-z0-9-]+\Z")
GITHUB_REPOSITORY = re.compile(r"[A-Za-z0-9._-]+\Z")
DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}\Z")


@dataclass(frozen=True)
class PastRun:
    id: str
    repository_url: str
    work_mode: str
    completed_at: str
    outcome: str
    summary: str
    steps: tuple[str, ...]
    pull_request_url: str | None = None
    preset: str | None = None
    request: str | None = None

    @property
    def repository_name(self) -> str:
        return urlsplit(self.repository_url).path.strip("/")


def _github_parts(value: object, *, pull_request: bool = False) -> list[str]:
    if not isinstance(value, str):
        raise TypeError("expected a GitHub URL")
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid GitHub URL") from exc
    parts = parsed.path.strip("/").split("/")
    if (
        parsed.scheme != "https"
        or host != "github.com"
        or parsed.username is not None
        or parsed.password is not None
        or port is not None
        or parsed.query
        or parsed.fragment
        or len(parts) != (4 if pull_request else 2)
        or not GITHUB_OWNER.fullmatch(parts[0])
        or not GITHUB_REPOSITORY.fullmatch(parts[1])
    ):
        raise ValueError("expected a public https://github.com/owner/repository URL")
    if pull_request and (parts[2] != "pull" or not parts[3].isdigit()):
        raise ValueError("expected a GitHub pull request URL")
    return parts


def _nonempty_text(record: dict, field: str) -> str:
    value = record.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    return value.strip()


def parse_past_runs(data: object) -> list[PastRun]:
    if not isinstance(data, list):
        raise TypeError("past runs must be a JSON list")

    runs: list[PastRun] = []
    seen_ids: set[str] = set()
    for index, raw in enumerate(data, start=1):
        try:
            if not isinstance(raw, dict):
                raise TypeError("entry must be an object")
            mode = _nonempty_text(raw, "work_mode")
            if mode not in {keys.WORK_MODE_PIPELINE, keys.WORK_MODE_AGENTIC}:
                raise ValueError("work_mode must be Automated pipeline or Agentic conversation")
            specific = {"preset"} if mode == keys.WORK_MODE_PIPELINE else {"request"}
            missing = (REQUIRED_FIELDS | specific) - raw.keys()
            extra = raw.keys() - (REQUIRED_FIELDS | OPTIONAL_FIELDS | specific)
            if missing or extra:
                raise ValueError(
                    f"missing fields: {sorted(missing)}; unexpected fields: {sorted(extra)}"
                )

            run_id = _nonempty_text(raw, "id")
            if run_id in seen_ids:
                raise ValueError(f"duplicate id: {run_id}")
            seen_ids.add(run_id)

            repository_url = _nonempty_text(raw, "repository_url")
            repository_parts = _github_parts(repository_url)
            completed_at = _nonempty_text(raw, "completed_at")
            if not DATE_PATTERN.fullmatch(completed_at):
                raise ValueError("completed_at must be YYYY-MM-DD")
            date.fromisoformat(completed_at)
            outcome = _nonempty_text(raw, "outcome")
            if outcome not in OUTCOMES:
                raise ValueError("outcome must be completed, failed, or stopped")
            summary = _nonempty_text(raw, "summary")
            steps = raw["steps"]
            if not isinstance(steps, list) or not steps:
                raise ValueError("steps must be a nonempty list of text")
            validated_steps = tuple(_nonempty_text({"step": step}, "step") for step in steps)
            pull_request_url = raw.get("pull_request_url")
            if pull_request_url is not None:
                pull_parts = _github_parts(pull_request_url, pull_request=True)
                if pull_parts[:2] != repository_parts:
                    raise ValueError("pull_request_url must belong to the repository")

            preset = request = None
            if mode == keys.WORK_MODE_PIPELINE:
                preset = _nonempty_text(raw, "preset")
                if preset not in {"fast", "quality"}:
                    raise ValueError("preset must be fast or quality")
            else:
                request = _nonempty_text(raw, "request")

            runs.append(
                PastRun(
                    id=run_id,
                    repository_url=repository_url,
                    work_mode=mode,
                    completed_at=completed_at,
                    outcome=outcome,
                    summary=summary,
                    steps=validated_steps,
                    pull_request_url=pull_request_url,
                    preset=preset,
                    request=request,
                )
            )
        except (ValueError, TypeError) as exc:
            raise ValueError(f"Past run #{index}: {exc}") from exc
    return runs


def load_past_runs(path: Path | None = None) -> list[PastRun]:
    source = path or files("osa_web").joinpath("data", "past_runs.json")
    return parse_past_runs(json.loads(source.read_text(encoding="utf-8")))

from __future__ import annotations

import re

from osa_web.osa_tool.models import ParsedOsaOutput

REPORT_PATTERN = re.compile(r"PDF report successfully created in (\/.*.pdf)")
ABOUT_PATTERN = re.compile(
    r"(.*You can add the following.*|.*- Description:.*|.*- Homepage:.*|"
    r".*- Topics:.*|.*Please review and add them to your repository.*)"
)
PR_PATTERN = re.compile(r".*pull request created successfully: (\S*)")
ERROR_PATTERN = re.compile(r"\bERROR\s+(?:\[[^]]+\]\s*-\s*)?(.*)")
PEPY_DOWNLOAD_ERROR = re.compile(
    r"\[PyPiInspector\] (?:Pepy request failed\b|Failed to fetch downloads from pepy\.tech\b)"
)


def parse_output_line(line: str, parsed: ParsedOsaOutput | None = None) -> ParsedOsaOutput:
    parsed = parsed or ParsedOsaOutput()

    if match := REPORT_PATTERN.search(line):
        report_path = match.group(1)
        parsed.report_paths.append(report_path)
        parsed.report_filenames.append(report_path.split("/")[-1])

    if ABOUT_PATTERN.search(line):
        parsed.about_section += line + "\n\n"

    if match := PR_PATTERN.search(line):
        parsed.pr_link = match.group(1)

    if match := ERROR_PATTERN.search(line):
        detail = match.group(1).strip()[:1000]
        if PEPY_DOWNLOAD_ERROR.search(detail):
            parsed.nonfatal_errors.append(detail)
        else:
            parsed.error_lines.append(detail)

    return parsed


def result_message(exit_code: int, parsed: ParsedOsaOutput, last_line: str | None) -> str:
    """Describe the result without treating a zero exit code as proof of success."""
    if parsed.error_lines:
        if any(
            "Error code: 401" in line or "invalid_api_key" in line for line in parsed.error_lines
        ):
            return (
                "OSA reported an LLM authentication error (HTTP 401). "
                "Check the configured API key and see console output."
            )
        requirements_error = "Fatal error: Could not generate requirements."
        if any(requirements_error in line for line in parsed.error_lines) and all(
            requirements_error in line
            or ("pipreqs" in line and "returned non-zero exit status" in line)
            for line in parsed.error_lines
        ):
            return (
                "OSA finished, but requirements generation failed because pipreqs exited "
                "with an error. Other operations continued. See console output."
            )
        return "OSA reported errors during the run. See console output for details."
    if exit_code:
        return f"**Error running OSA tool**: `{last_line or f'exit code {exit_code}'}`"
    if parsed.nonfatal_errors:
        reason = (
            " (Pepy HTTP 401)"
            if any("status 401" in line for line in parsed.nonfatal_errors)
            else ""
        )
        message = (
            f"OSA completed, but package download counts were unavailable{reason}. "
            "See console output."
        )
        if parsed.pr_link:
            message += f" **Pull Request created**: {parsed.pr_link}"
        return message
    if parsed.pr_link:
        return f"Everything is alright! **Pull Request created**: {parsed.pr_link}"
    return "Everything is alright!"

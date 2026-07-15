from __future__ import annotations

import re

from osa_web.osa_tool.models import ParsedOsaOutput

REPORT_PATTERN = re.compile(r"PDF report successfully created in (\/.*.pdf)")
ABOUT_PATTERN = re.compile(
    r"(.*You can add the following.*|.*- Description:.*|.*- Homepage:.*|"
    r".*- Topics:.*|.*Please review and add them to your repository.*)"
)
PR_PATTERN = re.compile(r".*pull request created successfully: (\S*)")


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

    return parsed

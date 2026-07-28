from unittest import TestCase

from osa_web.osa_tool.output_parser import parse_output_line


class OutputParserTests(TestCase):
    def test_collects_report_path_and_filename(self) -> None:
        parsed = parse_output_line(
            "PDF report successfully created in /tmp/run/example_report.pdf"
        )

        self.assertEqual(parsed.report_paths, ["/tmp/run/example_report.pdf"])
        self.assertEqual(parsed.report_filenames, ["example_report.pdf"])

    def test_collects_about_section_and_pull_request(self) -> None:
        parsed = parse_output_line("You can add the following metadata:")
        parse_output_line("- Description: Web UI for OSA", parsed)
        parse_output_line("pull request created successfully: https://github.com/org/repo/pull/1", parsed)

        self.assertIn("- Description: Web UI for OSA", parsed.about_section)
        self.assertEqual(parsed.pr_link, "https://github.com/org/repo/pull/1")

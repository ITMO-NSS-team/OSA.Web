from unittest import TestCase

from osa_web.osa_tool.output_parser import parse_output_line, result_message


class OutputParserTests(TestCase):
    def test_failed_requirements_remain_visible_after_success_banner(self) -> None:
        parsed = parse_output_line(
            "ERROR [06:33:47] - Fatal error: Could not generate requirements."
        )
        parse_output_line(
            "ERROR [06:33:47] - Command '['pipreqs', '--force']' returned non-zero exit status 1.",
            parsed,
        )
        parse_output_line("INFO - README.md generated", parsed)
        parse_output_line("All operations completed successfully", parsed)

        self.assertEqual(len(parsed.error_lines), 2)
        self.assertIn("requirements generation failed", result_message(0, parsed, None))
        self.assertNotIn("Everything is alright", result_message(0, parsed, None))

    def test_pepy_401_is_nonfatal_after_successful_run(self) -> None:
        parsed = parse_output_line(
            "[05:39:07] ERROR [05:39:07] - [PyPiInspector] "
            "Pepy request failed for mnist_synthetic (status 401)"
        )
        parse_output_line("PDF report successfully created in /tmp/run/work_summary.pdf", parsed)
        parse_output_line("All operations completed successfully", parsed)

        self.assertEqual(parsed.error_lines, [])
        self.assertEqual(len(parsed.nonfatal_errors), 1)
        self.assertEqual(len(parsed.report_paths), 1)
        self.assertIn(
            "package download counts were unavailable (Pepy HTTP 401)",
            result_message(0, parsed, "All operations completed successfully"),
        )

    def test_pepy_warning_does_not_hide_actual_failure(self) -> None:
        parsed = parse_output_line("ERROR - [PyPiInspector] Pepy request failed (status 401)")
        parse_output_line("ERROR - Error code: 401 - invalid_api_key", parsed)

        self.assertIn("LLM authentication error", result_message(0, parsed, None))

    def test_error_log_overrides_successful_exit_code(self) -> None:
        parsed = parse_output_line(
            "[05:09:18] ERROR [05:09:18] - Error code: 401 - invalid_api_key"
        )
        parse_output_line("All operations completed successfully", parsed)

        self.assertEqual(len(parsed.error_lines), 1)
        self.assertIn(
            "HTTP 401", result_message(0, parsed, "All operations completed successfully")
        )

    def test_warning_does_not_override_success(self) -> None:
        parsed = parse_output_line("WARNING Model failed; trying fallback")

        self.assertFalse(parsed.error_lines)
        self.assertEqual(result_message(0, parsed, None), "Everything is alright!")

    def test_collects_report_path_and_filename(self) -> None:
        parsed = parse_output_line("PDF report successfully created in /tmp/run/example_report.pdf")

        self.assertEqual(parsed.report_paths, ["/tmp/run/example_report.pdf"])
        self.assertEqual(parsed.report_filenames, ["example_report.pdf"])

    def test_collects_about_section_and_pull_request(self) -> None:
        parsed = parse_output_line("You can add the following metadata:")
        parse_output_line("- Description: Web UI for OSA", parsed)
        parse_output_line(
            "pull request created successfully: https://github.com/org/repo/pull/1", parsed
        )

        self.assertIn("- Description: Web UI for OSA", parsed.about_section)
        self.assertEqual(parsed.pr_link, "https://github.com/org/repo/pull/1")

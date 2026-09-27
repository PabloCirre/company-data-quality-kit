import contextlib
import csv
import importlib.util
import io
import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from company_data_quality import KitError, report_csv, validate_csv
from company_data_quality.cli import main

spec = importlib.util.spec_from_file_location("fixture_generator", ROOT / "examples" / "generate_fixture.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

REQUIRED = ["company_id", "company_name", "country_code"]
FORMATS = {"country_code": "country_code_alpha2", "website": "url_http", "email": "email_ascii", "observed_at": "date_iso"}


class CsvQualityTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.directory = Path(self.directory.name)

    def file(self, content, name="input.csv"):
        path = self.directory / name
        path.write_bytes(content.encode("utf-8") if isinstance(content, str) else content)
        return path

    def assert_code(self, code, content, **options):
        with self.assertRaises(KitError) as raised:
            validate_csv(self.file(content), **options)
        self.assertEqual(raised.exception.code, code)

    def fixture_report(self, filename="synthetic_company_data_comma.csv"):
        return validate_csv(ROOT / "fixtures" / filename, required_fields=REQUIRED, formats=FORMATS)

    def test_expected_fixture_aggregates(self):
        report = self.fixture_report()
        self.assertEqual(report["summary"], {
            "data_records": 12, "column_count": 8, "blank_records_skipped": 0,
            "required_column_count": 3, "format_rule_count": 4,
            "required_complete_records": 9, "missing_required_cells": 3,
            "format_failed_cells": 8, "exact_duplicate_records_beyond_first": 1,
            "exact_duplicate_groups": 1,
        })
        self.assertEqual([c["format_failed"] for c in report["columns"]], [0, 0, 1, 2, 3, 2, 0, 0])
        self.assertEqual(report["columns"][1]["completeness_pct"], 83.33)

    def test_semicolon_bom_equals_comma(self):
        comma = self.fixture_report()
        semicolon = self.fixture_report("synthetic_company_data_semicolon_bom.csv")
        self.assertEqual(semicolon["input_format"]["delimiter"], "semicolon")
        self.assertEqual(comma["summary"], semicolon["summary"])
        self.assertEqual(comma["columns"], semicolon["columns"])

    def test_utf8_non_ascii_and_quoted_newline(self):
        report = validate_csv(self.file('\ufeffid;name\n1;"Synthétique, España\nAbteilung"\n'))
        self.assertEqual(report["summary"]["data_records"], 1)
        self.assertEqual(report["columns"][1]["present"], 1)

    def test_delimiter_quoted_inside_header(self):
        report = validate_csv(self.file('"id,identifier";name\n1;Synthetic\n'))
        self.assertEqual(report["input_format"]["delimiter"], "semicolon")

    def test_ambiguous_header_requires_explicit_separator(self):
        self.assert_code("ambiguous_delimiter_use_explicit_option", "id,name;extra\n1,Test;value\n")
        report = validate_csv(self.file("id,name;extra\n1,Test;value\n"), delimiter="comma")
        self.assertEqual(report["summary"]["column_count"], 2)

    def test_single_column_with_explicit_separator(self):
        report = validate_csv(self.file("id\n1\n"), delimiter="comma")
        self.assertEqual(report["summary"]["data_records"], 1)

    def test_ragged_short_and_long_fail_without_partial_report(self):
        for value in ("id,name\n1,Synthetic\n2\n", "id,name\n1,Synthetic,extra\n"):
            with self.subTest(value=value):
                self.assert_code("ragged_record", value)

    def test_duplicate_trimmed_headers(self):
        self.assert_code("duplicate_headers", "id, id \n1,2\n")

    def test_missing_or_control_header(self):
        self.assert_code("invalid_header", "id,\n1,2\n")
        self.assert_code("invalid_header", 'id,"name\nextra"\n1,2\n')

    def test_empty_and_header_only(self):
        self.assert_code("empty_csv", "")
        self.assert_code("no_data_records", "id,name\n")
        self.assert_code("no_data_records", "id,name\n\n")

    def test_unclosed_quote_and_invalid_utf8(self):
        self.assert_code("invalid_csv_or_field_too_large", 'id,name\n1,"unterminated\n')
        self.assert_code("input_not_utf8", b"id,name\n1,\xff\n")

    def test_exact_duplicates_preserve_case_and_whitespace(self):
        report = validate_csv(self.file("id,name\n1,Synthetic\n1,Synthetic\n1,Synthetic\n1, Synthetic\n1,synthetic\n"))
        self.assertEqual(report["summary"]["exact_duplicate_records_beyond_first"], 2)
        self.assertEqual(report["summary"]["exact_duplicate_groups"], 1)

    def test_blank_records_are_not_empty_cells(self):
        report = validate_csv(self.file("id,name\n\n1,Synthetic\n,\n"), required_fields=["id"])
        self.assertEqual(report["summary"]["data_records"], 2)
        self.assertEqual(report["summary"]["blank_records_skipped"], 1)
        self.assertEqual(report["summary"]["missing_required_cells"], 1)

    def test_missingness_is_trimmed_but_na_and_zero_are_present(self):
        report = validate_csv(self.file('id,name\n1,"   "\n2,N/A\n3,0\n'), required_fields=["name"])
        self.assertEqual(report["columns"][1]["present"], 2)
        self.assertEqual(report["columns"][1]["missing"], 1)

    def test_mixed_date_formats_and_real_calendar(self):
        report = validate_csv(self.file("id,date\n1,2024-02-29\n2,2026-02-29\n3,27/09/2026\n4,20260927\n5,\n"), formats={"date": "date_iso"})
        column = report["columns"][1]
        self.assertEqual((column["format_checked"], column["format_passed"], column["format_failed"], column["missing"]), (4, 1, 3, 1))

    def test_rules_are_limited_not_registry_validation(self):
        report = validate_csv(self.file("id,country\n1,ZZ\n2,es\n3,ESP\n"), formats={"country": "country_code_alpha2"})
        self.assertEqual(report["columns"][1]["format_passed"], 1)  # ZZ has the required shape only.

    def test_email_is_syntax_only_and_makes_no_network_calls(self):
        with patch.object(socket, "socket", side_effect=AssertionError("network forbidden")), patch.object(socket, "getaddrinfo", side_effect=AssertionError("DNS forbidden")):
            report = validate_csv(self.file("id,email\n1,not-a-real-mailbox@reserved.example\n2,a..b@reserved.example\n"), formats={"email": "email_ascii"})
        self.assertEqual(report["columns"][1]["format_passed"], 1)
        self.assertEqual(report["columns"][1]["format_failed"], 1)
        self.assertTrue(any("No email deliverability" in item for item in report["limitations"]))
        self.assertNotIn("deliverable", json.dumps(report))

    def test_url_checks_credentials_ports_and_scheme(self):
        report = validate_csv(self.file("id,url\n1,https://company.example/path\n2,https://name:password@company.example\n3,https://company.example:99999\n4,ftp://company.example\n5,https://bad_domain.example\n"), formats={"url": "url_http"})
        self.assertEqual(report["columns"][1]["format_failed"], 4)

    def test_configuration_must_match_and_is_never_echoed(self):
        self.assert_code("configured_column_missing", "id,name\n1,Synthetic\n", required_fields=["private@reserved.example"])
        self.assert_code("unknown_format_rule", "id,name\n1,Synthetic\n", formats={"name": "secret-format"})

    def test_reports_do_not_include_values_paths_or_arbitrary_headers(self):
        secret = "private-contact@reserved.example"
        path = self.file(f"id,{secret}\n1,{secret}\n", name=secret + ".csv")
        report = validate_csv(path)
        for output in (json.dumps(report), report_csv(report)):
            self.assertNotIn(secret, output)
            self.assertNotIn(str(path), output)

    def test_cli_structural_error_has_no_sensitive_row(self):
        secret = "private-contact@reserved.example"
        path = self.file(f"id,name\n1,Synthetic\n2,{secret},extra\n")
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main([str(path)])
        self.assertEqual(code, 2)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(json.loads(stderr.getvalue()), {"status": "error", "error_code": "ragged_record"})

    def test_cli_bad_arguments_are_redacted(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(["--unknown", "private-contact@reserved.example"])
        self.assertEqual(code, 2)
        self.assertNotIn("private-contact", stdout.getvalue() + stderr.getvalue())

    def test_cli_outputs_aggregates_exit_codes_and_refuses_overwrite(self):
        source = self.file("id,name\n1,Synthetic\n1,Synthetic\n")
        json_out, csv_out = self.directory / "report.json", self.directory / "report.csv"
        options = [str(source), "--json-out", str(json_out), "--csv-out", str(csv_out)]
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main(options), 1)
            before = json_out.read_bytes()
            self.assertEqual(main(options), 2)
            self.assertEqual(json_out.read_bytes(), before)
            self.assertEqual(main(options + ["--overwrite"]), 1)
        self.assertEqual(json.loads(json_out.read_text())["summary"]["data_records"], 2)
        records = list(csv.reader(io.StringIO(csv_out.read_text())))
        self.assertEqual(records[0], ["section", "column_id", "metric", "value"])

    def test_cli_never_overwrites_input_and_rejects_shared_destination(self):
        source = self.file("id,name\n1,Synthetic\n")
        before = source.read_bytes()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(main([str(source), "--json-out", str(source), "--overwrite"]), 2)
            out = str(self.directory / "both.txt")
            self.assertEqual(main([str(source), "--json-out", out, "--csv-out", out]), 2)
        self.assertEqual(source.read_bytes(), before)

    def test_no_rules_means_no_required_row_certificate(self):
        report = validate_csv(self.file("id,name\n1,\n"))
        self.assertEqual(report["status"], "checks_passed")
        self.assertIsNone(report["summary"]["required_complete_records"])
        self.assertEqual(report["summary"]["format_rule_count"], 0)

    def test_fixture_is_deterministic_and_fictional(self):
        for filename, sep, bom in [("synthetic_company_data_comma.csv", ",", False), ("synthetic_company_data_semicolon_bom.csv", ";", True)]:
            expected = generator.fixture_bytes(sep, bom)
            self.assertEqual(expected, generator.fixture_bytes(sep, bom))
            self.assertEqual((ROOT / "fixtures" / filename).read_bytes(), expected)
        self.assertTrue(all(row[-1] == "true" and row[-2] == "" for row in generator.fixture_rows()))
        self.assertTrue(all(".example" in row[4] for row in generator.fixture_rows() if "@" in row[4]))

    def test_stored_expected_reports_match(self):
        report = self.fixture_report()
        self.assertEqual(json.loads((ROOT / "examples" / "expected_report.json").read_text()), report)
        self.assertEqual((ROOT / "examples" / "expected_report.csv").read_bytes(), report_csv(report).encode("utf-8"))

    def test_direct_script_and_module(self):
        source = self.file("id,name\n1,Synthetic\n")
        commands = [([sys.executable, str(ROOT / "validate_csv.py"), str(source)], self.directory),
                    ([sys.executable, "-m", "company_data_quality", str(source)], ROOT)]
        for command, cwd in commands:
            result = subprocess.run(command, cwd=cwd, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "checks_passed")


if __name__ == "__main__":
    unittest.main()

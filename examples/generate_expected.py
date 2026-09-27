"""Regenerate bundled aggregate examples from the CC0 synthetic fixture only."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from company_data_quality import report_csv, validate_csv


def main():
    report = validate_csv(
        ROOT / "fixtures" / "synthetic_company_data_comma.csv",
        required_fields=["company_id", "company_name", "country_code"],
        formats={"country_code": "country_code_alpha2", "website": "url_http", "email": "email_ascii", "observed_at": "date_iso"},
    )
    (ROOT / "examples" / "expected_report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    (ROOT / "examples" / "expected_report.csv").write_text(report_csv(report), encoding="utf-8", newline="\n")
    print("Wrote deterministic aggregate reports from the synthetic fixture only.")


if __name__ == "__main__":
    main()

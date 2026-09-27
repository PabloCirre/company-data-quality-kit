"""Regenerate artificial examples deterministically; no random seed or network."""

import csv
import io
from pathlib import Path

HEADERS = ["company_id", "company_name", "country_code", "website", "email", "observed_at", "phone", "synthetic"]


def fixture_rows():
    countries = ["ES", "IT", "ES", "DE", "FR", "es", "GB", "GB", "", "NL", "PL", "PT"]
    rows = []
    for i, country in enumerate(countries, 1):
        rows.append([f"SYN-{i:03d}", f"Synthetic Example Company {i:03d}", country,
                     f"https://company-{i:03d}.example", f"contact@company-{i:03d}.example",
                     "2026-09-01", "", "true"])
    rows[1][1] = 'Synthetic Example 002, lab; "division"'
    rows[2] = list(rows[0])
    rows[3][1], rows[3][4] = "", "not-an-email"
    rows[4][3:6] = ["not a url", "", "2026-02-30"]
    rows[6][3:6] = ["", "a..b@company-007.example", "01/09/2026"]
    rows[7][1] = "Synthetic Example\nDivision 008"
    rows[8][4] = ".leading@company-009.example"
    rows[9][1], rows[9][3], rows[9][5] = "   ", "ftp://company-010.example", ""
    return rows


def fixture_bytes(delimiter=",", bom=False):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, delimiter=delimiter, lineterminator="\n")
    writer.writerow(HEADERS)
    writer.writerows(fixture_rows())
    return stream.getvalue().encode("utf-8-sig" if bom else "utf-8")


def main():
    root = Path(__file__).resolve().parents[1] / "fixtures"
    root.mkdir(exist_ok=True)
    (root / "synthetic_company_data_comma.csv").write_bytes(fixture_bytes())
    (root / "synthetic_company_data_semicolon_bom.csv").write_bytes(fixture_bytes(";", True))
    print("Wrote the two deterministic synthetic fixtures (12 records each).")


if __name__ == "__main__":
    main()

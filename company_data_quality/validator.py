"""Deterministic CSV measurements; no requests, DNS, SMTP, or registry lookups."""

from __future__ import annotations

import csv
import io
import re
from datetime import date
from pathlib import Path
from typing import Callable, Iterable, Mapping
from urllib.parse import urlsplit


class KitError(Exception):
    """A fixed diagnostic code that never incorporates input data or paths."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def _domain(value: str) -> bool:
    labels = value.split(".")
    return (
        len(value) <= 253
        and len(labels) >= 2
        and all(re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", x) for x in labels)
        and not labels[-1].isdigit()
    )


def _email(value: str) -> bool:
    if len(value) > 254 or value.count("@") != 1:
        return False
    local, domain = value.rsplit("@", 1)
    return bool(
        1 <= len(local) <= 64
        and not local.startswith(".")
        and not local.endswith(".")
        and ".." not in local
        and re.fullmatch(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+", local)
        and _domain(domain)
    )


def _url(value: str) -> bool:
    if any(c.isspace() or ord(c) < 32 for c in value):
        return False
    try:
        parts = urlsplit(value)
        return bool(
            parts.scheme in {"http", "https"}
            and parts.hostname
            and _domain(parts.hostname)
            and parts.username is None
            and parts.password is None
            and (parts.port is None or 1 <= parts.port <= 65535)
        )
    except ValueError:
        return False


def _date(value: str) -> bool:
    if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


FORMAT_CHECKS: dict[str, Callable[[str], bool]] = {
    "email_ascii": _email,
    "url_http": _url,
    "date_iso": _date,
    "country_code_alpha2": lambda value: bool(re.fullmatch(r"[A-Z]{2}", value)),
}
DELIMITERS = {"comma": ",", "semicolon": ";"}
LIMITATIONS = [
    "Measures only this supplied file; does not measure market or registry coverage.",
    "Format checks are deliberately limited syntax checks, not correctness certificates.",
    "No email deliverability, DNS, SMTP, phone, consent, or registry verification is performed.",
    "Exact duplicates use all parsed field values unchanged; entity matching is not performed.",
    "Reports contain counts and column positions, not input values, headers, or file paths.",
    "Aggregates are not an anonymization guarantee; review small groups before sharing.",
]


def _open(path: Path):
    return path.open("r", encoding="utf-8-sig", newline="")


def _choose_delimiter(path: Path, requested: str) -> str:
    if requested in DELIMITERS:
        return DELIMITERS[requested]
    if requested != "auto":
        raise KitError("invalid_delimiter_option")
    candidates = []
    any_record = False
    for delimiter in DELIMITERS.values():
        try:
            with _open(path) as stream:
                reader = csv.reader(stream, delimiter=delimiter, strict=True)
                first = next(reader, None)
                any_record |= first is not None
                if first is not None and len(first) > 1:
                    candidates.append(delimiter)
        except csv.Error:
            # A quoted header can be invalid with the incorrect delimiter.
            continue
    if not any_record:
        raise KitError("empty_csv")
    if len(candidates) != 1:
        raise KitError("ambiguous_delimiter_use_explicit_option")
    return candidates[0]


def validate_csv(
    path: str | Path,
    *,
    required_fields: Iterable[str] = (),
    formats: Mapping[str, str] | None = None,
    delimiter: str = "auto",
) -> dict:
    """Measure a UTF-8 CSV; raise KitError on structural/configuration failures.

    Headers are stripped and case-sensitive. Row values are stripped only for
    missingness and syntax; exact duplicate comparison keeps original whitespace.
    The in-memory duplicate counter retains parsed rows only for this call.
    """
    required = set(required_fields)
    formats = dict(formats or {})
    if any(rule not in FORMAT_CHECKS for rule in formats.values()):
        raise KitError("unknown_format_rule")
    try:
        source = Path(path)
        sep = _choose_delimiter(source, delimiter)
        with _open(source) as stream:
            reader = csv.reader(stream, delimiter=sep, strict=True)
            raw_headers = next(reader, None)
            if raw_headers is None:
                raise KitError("empty_csv")
            headers = [field.strip() for field in raw_headers]
            if not headers or any(not h or any(ord(c) < 32 for c in h) for h in headers):
                raise KitError("invalid_header")
            if len(set(headers)) != len(headers):
                raise KitError("duplicate_headers")
            if (required | set(formats)) - set(headers):
                raise KitError("configured_column_missing")
            columns = [
                {
                    "column_id": f"column_{i + 1}",
                    "required": header in required,
                    "format_rule": formats.get(header),
                    "present": 0,
                    "missing": 0,
                    "completeness_pct": 0.0,
                    "format_checked": 0,
                    "format_passed": 0,
                    "format_failed": 0,
                }
                for i, header in enumerate(headers)
            ]
            seen: dict[tuple[str, ...], int] = {}
            rows = blank = duplicates = duplicate_groups = required_complete = 0
            for row in reader:
                if not row:
                    blank += 1
                    continue
                if len(row) != len(headers):
                    raise KitError("ragged_record")
                rows += 1
                key = tuple(row)
                previous = seen.get(key, 0)
                seen[key] = previous + 1
                if previous:
                    duplicates += 1
                if previous == 1:
                    duplicate_groups += 1
                row_required_complete = True
                for value, column in zip(row, columns):
                    cleaned = value.strip()
                    if not cleaned:
                        column["missing"] += 1
                        if column["required"]:
                            row_required_complete = False
                    else:
                        column["present"] += 1
                        rule = column["format_rule"]
                        if rule:
                            column["format_checked"] += 1
                            if FORMAT_CHECKS[rule](cleaned):
                                column["format_passed"] += 1
                            else:
                                column["format_failed"] += 1
                required_complete += int(row_required_complete)
            if rows == 0:
                raise KitError("no_data_records")
            for column in columns:
                column["completeness_pct"] = round(column["present"] / rows * 100, 2)
            missing_required = sum(c["missing"] for c in columns if c["required"])
            failed_formats = sum(c["format_failed"] for c in columns)
            return {
                "schema_version": "1.0",
                "status": "needs_review" if missing_required or failed_formats or duplicates else "checks_passed",
                "input_format": {
                    "delimiter": "comma" if sep == "," else "semicolon",
                    "decoder": "utf-8-sig",
                },
                "summary": {
                    "data_records": rows,
                    "column_count": len(columns),
                    "blank_records_skipped": blank,
                    "required_column_count": len(required),
                    "format_rule_count": len(formats),
                    "required_complete_records": required_complete if required else None,
                    "missing_required_cells": missing_required,
                    "format_failed_cells": failed_formats,
                    "exact_duplicate_records_beyond_first": duplicates,
                    "exact_duplicate_groups": duplicate_groups,
                },
                "columns": columns,
                "limitations": list(LIMITATIONS),
            }
    except UnicodeError:
        raise KitError("input_not_utf8") from None
    except csv.Error:
        raise KitError("invalid_csv_or_field_too_large") from None
    except OSError:
        raise KitError("input_unreadable") from None


def report_csv(report: dict) -> str:
    """Flatten only generated aggregate metrics to an Excel-readable CSV."""
    output = io.StringIO(newline="")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(["section", "column_id", "metric", "value"])
    writer.writerow(["report", "", "status", report["status"]])
    for metric, value in report["summary"].items():
        writer.writerow(["summary", "", metric, value])
    for column in report["columns"]:
        for metric, value in column.items():
            if metric != "column_id":
                writer.writerow(["column", column["column_id"], metric, value])
    return output.getvalue()

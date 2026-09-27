"""Safe CLI: fixed diagnostics, local files, and aggregate-only output."""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from .validator import FORMAT_CHECKS, KitError, report_csv, validate_csv


class SafeParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse's usual message can echo paths or user-supplied field names.
        raise KitError("invalid_cli_arguments_use_help")


def _atomic_write(path: Path, content: str, overwrite: bool) -> None:
    pending = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=path.parent, delete=False) as stream:
            pending = Path(stream.name)
            stream.write(content)
        if overwrite:
            os.replace(pending, path)
        else:
            # A hard link publishes the complete temporary file without replacing
            # an existing destination, even if another process just created it.
            os.link(pending, path)
        if pending.exists():
            pending.unlink()
    finally:
        if pending is not None and pending.exists():
            pending.unlink()


def main(argv=None) -> int:
    parser = SafeParser(description="Measure a local UTF-8 CSV; emit aggregate counts only. No network or contact verification.")
    parser.add_argument("input", help="Local CSV path (never included in reports)")
    parser.add_argument("--delimiter", choices=["auto", "comma", "semicolon"], default="auto")
    parser.add_argument("--required", action="append", default=[], metavar="FIELD", help="Repeat for each required column; names are case-sensitive")
    parser.add_argument("--format", action="append", default=[], metavar="FIELD=RULE", help="Repeat; rules: " + ", ".join(FORMAT_CHECKS))
    parser.add_argument("--json-out", type=Path, help="Optional aggregate JSON file")
    parser.add_argument("--csv-out", type=Path, help="Optional aggregate CSV file")
    parser.add_argument("--overwrite", action="store_true", help="Replace existing report files; never the input")
    try:
        args = parser.parse_args(argv)
        formats = {}
        for item in args.format:
            if "=" not in item:
                raise KitError("invalid_format_configuration")
            field, rule = item.rsplit("=", 1)
            if not field or field in formats or rule not in FORMAT_CHECKS:
                raise KitError("invalid_format_configuration")
            formats[field] = rule
        destinations = [p.resolve() for p in (args.json_out, args.csv_out) if p is not None]
        if len(set(destinations)) != len(destinations) or Path(args.input).resolve() in destinations:
            raise KitError("output_path_conflict")
        if any(not p.parent.is_dir() or p.is_dir() for p in destinations):
            raise KitError("output_directory_unavailable")
        if not args.overwrite and any(p.exists() for p in destinations):
            raise KitError("output_exists_use_overwrite")
        result = validate_csv(args.input, required_fields=args.required, formats=formats, delimiter=args.delimiter)
        content = json.dumps(result, ensure_ascii=True, indent=2) + "\n"
        if args.json_out:
            _atomic_write(args.json_out.resolve(), content, args.overwrite)
        if args.csv_out:
            _atomic_write(args.csv_out.resolve(), report_csv(result), args.overwrite)
        sys.stdout.write(content)
        return 1 if result["status"] == "needs_review" else 0
    except KitError as error:
        sys.stderr.write(json.dumps({"status": "error", "error_code": error.code}) + "\n")
        return 2
    except OSError:
        sys.stderr.write('{"status": "error", "error_code": "output_or_path_unavailable"}\n')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

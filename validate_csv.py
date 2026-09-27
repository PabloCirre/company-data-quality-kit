"""Run directly from any working directory: python /path/to/validate_csv.py ..."""

from company_data_quality.cli import main

if __name__ == "__main__":
    raise SystemExit(main())

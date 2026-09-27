"""Local, aggregate-only CSV checks. Code and documentation: MIT."""

from .validator import KitError, report_csv, validate_csv

__all__ = ["KitError", "report_csv", "validate_csv"]
__version__ = "1.0.0"

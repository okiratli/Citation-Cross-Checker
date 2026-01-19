"""Citation Cross-Checker: Verify citations match bibliography entries."""

from .checker import CitationChecker
from .models import CheckResult, Citation, BibEntry, YearMismatch

__version__ = "1.0.0"
__all__ = ["CitationChecker", "CheckResult", "Citation", "BibEntry", "YearMismatch"]

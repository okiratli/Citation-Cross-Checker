"""Data models for citations and bibliography entries."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Citation:
    """Represents an in-text citation."""

    raw_text: str
    authors: List[str]
    year: Optional[str] = None
    page: Optional[str] = None
    number: Optional[int] = None  # For numeric citations like [1]
    position: int = 0  # Character position in document
    citation_type: str = "unknown"  # author-year, mla, numeric, ieee

    def __str__(self):
        return self.raw_text

    def matches_bib(self, bib_entry: 'BibEntry') -> bool:
        """Check if this citation matches a bibliography entry."""
        if self.citation_type == "numeric" or self.citation_type == "ieee":
            return self.number == bib_entry.number

        # For author-year citations (APA, Harvard, Chicago, MLA)
        if not self.authors or not bib_entry.authors:
            return False

        # Normalize author names for comparison
        # Extract last names and compare (case-insensitive)
        def normalize_name(name):
            """Extract last name from various formats."""
            # Remove common punctuation
            name = name.replace('.', '').replace(',', '').strip()
            # Get the last word (usually the last name)
            words = name.split()
            if words:
                return words[-1].lower()
            return name.lower()

        # Check if first author matches (handle "et al." cases)
        citation_first = normalize_name(self.authors[0])
        bib_first = normalize_name(bib_entry.authors[0])

        # Match if the last names are the same or one contains the other
        if citation_first != bib_first:
            # Allow partial match (e.g., "Smith-Jones" matches "Smith")
            if citation_first not in bib_first and bib_first not in citation_first:
                return False

        # If year is present in both, it must match
        if self.year and bib_entry.year:
            return self.year == bib_entry.year

        return True

    def authors_match_bib(self, bib_entry: 'BibEntry') -> bool:
        """Check if authors match, ignoring year (for year mismatch detection)."""
        if self.citation_type == "numeric" or self.citation_type == "ieee":
            return False  # Numeric citations don't have year mismatches

        if not self.authors or not bib_entry.authors:
            return False

        def normalize_name(name):
            """Extract last name from various formats."""
            name = name.replace('.', '').replace(',', '').strip()
            words = name.split()
            if words:
                return words[-1].lower()
            return name.lower()

        # Normalize all author names
        citation_authors = [normalize_name(a) for a in self.authors]
        bib_authors = [normalize_name(a) for a in bib_entry.authors]

        # If citation has only 1 author but bib has multiple, assume "et al." case
        # Only check first author match (must be exact, not substring)
        if len(self.authors) == 1 and len(bib_entry.authors) > 1:
            citation_first = citation_authors[0]
            bib_first = bib_authors[0]
            # Exact match only - prevents "Lee" from matching "Leeds"
            return citation_first == bib_first

        # If citation has multiple authors, ALL must match (in any order)
        # This ensures "(Brutger and Clark)" doesn't match "Brutger and Kertzer"
        if len(citation_authors) != len(bib_authors):
            return False

        # Check if all citation authors are in bib authors (order may differ)
        # Require exact matches only
        for cit_author in citation_authors:
            if cit_author not in bib_authors:
                return False

        return True


@dataclass
class BibEntry:
    """Represents a bibliography entry."""

    raw_text: str
    authors: List[str]
    year: Optional[str] = None
    title: Optional[str] = None
    number: Optional[int] = None  # For numbered references like [1]
    position: int = 0  # Line number in bibliography
    entry_type: str = "unknown"  # author-year, mla, numeric, ieee

    def __str__(self):
        return self.raw_text

    def get_key(self) -> str:
        """Generate a unique key for this entry."""
        if self.number is not None:
            return f"[{self.number}]"
        if self.authors and self.year:
            first_author = self.authors[0].split(',')[0].split()[-1]
            return f"{first_author}, {self.year}"
        return self.raw_text[:50]


@dataclass
class YearMismatch:
    """Represents a potential year mismatch between citation and bibliography."""

    citation: Citation
    bib_entry: BibEntry

    def __str__(self):
        return f"Citation {self.citation.raw_text} vs Bibliography {self.bib_entry.get_key()}"


@dataclass
class CheckResult:
    """Results of citation cross-checking."""

    citations: List[Citation]
    bib_entries: List[BibEntry]
    missing_bib_entries: List[Citation]  # Citations without matching bib entries
    uncited_references: List[BibEntry]  # Bib entries never cited
    year_mismatches: List[YearMismatch]  # Potential year mismatches

    def has_issues(self) -> bool:
        """Return True if any inconsistencies were found."""
        return bool(self.missing_bib_entries or self.uncited_references or self.year_mismatches)

    def generate_report(self, use_colors: bool = True) -> str:
        """Generate a human-readable report."""
        from .formatters import ReportFormatter
        formatter = ReportFormatter(use_colors=use_colors)
        return formatter.format_result(self)

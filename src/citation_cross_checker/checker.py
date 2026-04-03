"""Main citation cross-checking logic."""

import re
from typing import Optional
from .models import CheckResult, Citation, BibEntry, YearMismatch, AuthorMismatch
from .parsers import CitationParser, BibliographyParser
from .document_reader import DocumentReader


def _levenshtein(a: str, b: str) -> int:
    """Compute the Levenshtein edit distance between two strings."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        curr = [i]
        for j, cb in enumerate(b, 1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = curr
    return prev[-1]


def _normalize_last_name(name: str) -> str:
    """Extract and normalise the last name from an author string."""
    name = name.replace('.', '').replace(',', '').strip()
    words = name.split()
    return words[-1].lower() if words else name.lower()


class CitationChecker:
    """Main class for checking citation consistency."""

    def __init__(self):
        self.citation_parser = CitationParser()
        self.bib_parser = BibliographyParser()

    def check_document(
        self,
        text: str,
        bib_section_name: Optional[str] = None
    ) -> CheckResult:
        """
        Check a document for citation-bibliography consistency.

        Args:
            text: The full document text
            bib_section_name: Optional custom name for bibliography section

        Returns:
            CheckResult object with findings
        """
        # Parse bibliography entries first so we know where the section starts
        bib_entries, bib_text = self.bib_parser.parse(text, bib_section_name)

        # Parse citations from text BEFORE the bibliography section.
        # This prevents bibliography entries (e.g. "Hine DW and Montiel CJ (1999)")
        # from being mis-parsed as in-text citations.
        # Endnotes/footnotes appear before the bibliography, so they are still included.
        text_for_citations = self._text_before_bibliography(text, bib_section_name)
        citations = self.citation_parser.parse(text_for_citations)

        # Find citations without matching bibliography entries
        missing_bib_entries = self._find_missing_bib_entries(citations, bib_entries)

        # Find bibliography entries that are never cited
        uncited_references = self._find_uncited_references(citations, bib_entries)

        # Find potential year mismatches
        year_mismatches = self._find_year_mismatches(
            missing_bib_entries,
            uncited_references,
            citations,
            bib_entries
        )

        # Find potential author spelling mismatches
        author_mismatches = self._find_author_mismatches(
            missing_bib_entries,
            bib_entries,
            year_mismatches
        )

        return CheckResult(
            citations=citations,
            bib_entries=bib_entries,
            missing_bib_entries=missing_bib_entries,
            uncited_references=uncited_references,
            year_mismatches=year_mismatches,
            author_mismatches=author_mismatches
        )

    def check_file(
        self,
        file_path: str,
        bib_section_name: Optional[str] = None
    ) -> CheckResult:
        """
        Check a file for citation-bibliography consistency.

        Supports: .txt, .md, .docx, .pdf files

        Args:
            file_path: Path to the manuscript file (.txt, .md, .docx, .pdf)
            bib_section_name: Optional custom name for bibliography section

        Returns:
            CheckResult object with findings
        """
        text = DocumentReader.read_file(file_path)
        return self.check_document(text, bib_section_name)

    def _find_missing_bib_entries(
        self,
        citations: list[Citation],
        bib_entries: list[BibEntry]
    ) -> list[Citation]:
        """Find citations that don't have matching bibliography entries."""
        missing = []
        seen_citations = set()

        for citation in citations:
            # Check if this citation matches any bibliography entry
            has_match = False
            for bib_entry in bib_entries:
                if citation.matches_bib(bib_entry):
                    has_match = True
                    break

            if not has_match:
                # Create a unique key to avoid duplicates
                # Use authors and year to identify unique citations
                if citation.citation_type == "numeric":
                    citation_key = f"[{citation.number}]"
                else:
                    authors_key = ",".join(sorted(citation.authors)) if citation.authors else ""
                    citation_key = f"{authors_key}:{citation.year}"

                # Only add if we haven't seen this citation before
                if citation_key not in seen_citations:
                    missing.append(citation)
                    seen_citations.add(citation_key)

        return missing

    def _find_uncited_references(
        self,
        citations: list[Citation],
        bib_entries: list[BibEntry]
    ) -> list[BibEntry]:
        """Find bibliography entries that are never cited in the text."""
        uncited = []

        for bib_entry in bib_entries:
            # Check if this bibliography entry matches any citation
            is_cited = False
            for citation in citations:
                if citation.matches_bib(bib_entry):
                    is_cited = True
                    break

            if not is_cited:
                uncited.append(bib_entry)

        return uncited

    def _find_year_mismatches(
        self,
        missing_bib_entries: list[Citation],
        uncited_references: list[BibEntry],
        all_citations: list[Citation],
        all_bib_entries: list[BibEntry]
    ) -> list[YearMismatch]:
        """
        Find potential year mismatches.

        When a citation has no matching bibliography entry, check if there's
        a bibliography entry with the same authors but different year.
        This often happens with online-first publications that change year
        when officially published.
        """
        mismatches = []
        processed_pairs = set()

        # Check each missing citation for potential year mismatches
        for citation in missing_bib_entries:
            if not citation.year:
                continue  # Need a year to detect mismatch

            # Look for bibliography entries with matching authors but different years
            for bib_entry in all_bib_entries:
                if not bib_entry.year:
                    continue

                # Check if authors match but years don't
                if citation.authors_match_bib(bib_entry) and citation.year != bib_entry.year:
                    # Create a unique key to avoid duplicates
                    pair_key = (id(citation), id(bib_entry))
                    if pair_key not in processed_pairs:
                        mismatches.append(YearMismatch(
                            citation=citation,
                            bib_entry=bib_entry
                        ))
                        processed_pairs.add(pair_key)

        return mismatches

    def _find_author_mismatches(
        self,
        missing_bib_entries: list[Citation],
        all_bib_entries: list[BibEntry],
        year_mismatches: list[YearMismatch]
    ) -> list[AuthorMismatch]:
        """
        Find potential author name spelling mismatches.

        For each unmatched citation, look for a bibliography entry whose
        first-author last name differs by at most 2 characters (Levenshtein
        distance) and whose year matches (or is absent in one side).
        Pairs already flagged as year mismatches are excluded to avoid
        reporting the same pair twice.
        """
        mismatches = []
        processed_pairs = set()

        # Build a set of (citation id, bib id) pairs already covered by year mismatches
        year_mismatch_pairs = {(id(ym.citation), id(ym.bib_entry)) for ym in year_mismatches}

        for citation in missing_bib_entries:
            if citation.citation_type in ("numeric", "ieee"):
                continue
            if not citation.authors:
                continue

            cit_last = _normalize_last_name(citation.authors[0])

            for bib_entry in all_bib_entries:
                if not bib_entry.authors:
                    continue

                bib_last = _normalize_last_name(bib_entry.authors[0])

                # Skip exact matches (already handled by the main matching logic)
                if cit_last == bib_last:
                    continue

                # Skip if years are both present and differ (that's a year mismatch)
                if citation.year and bib_entry.year and citation.year != bib_entry.year:
                    continue

                dist = _levenshtein(cit_last, bib_last)
                if dist < 1 or dist > 2:
                    continue

                pair_key = (id(citation), id(bib_entry))
                if pair_key in year_mismatch_pairs or pair_key in processed_pairs:
                    continue

                mismatches.append(AuthorMismatch(
                    citation=citation,
                    bib_entry=bib_entry,
                    edit_distance=dist
                ))
                processed_pairs.add(pair_key)

        return mismatches

    def _text_before_bibliography(self, text: str, bib_section_name: Optional[str] = None) -> str:
        """Return the portion of the document before the bibliography section."""
        headers = [bib_section_name] if bib_section_name else self.bib_parser.bib_headers
        for header in headers:
            if not header:
                continue
            pattern = r'^' + re.escape(header) + r'\s*:?\s*$'
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
            if match:
                return text[:match.start()]
        return text

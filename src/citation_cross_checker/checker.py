"""Main citation cross-checking logic."""

from typing import Optional
from .models import CheckResult, Citation, BibEntry, YearMismatch
from .parsers import CitationParser, BibliographyParser
from .document_reader import DocumentReader


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
        # Parse citations from full text (includes main text AND endnotes)
        # Note: For papers with endnotes, citations appear in the endnotes section,
        # so we parse the entire document to capture all citations
        citations = self.citation_parser.parse(text)

        # Parse bibliography entries
        bib_entries, bib_text = self.bib_parser.parse(text, bib_section_name)

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

        return CheckResult(
            citations=citations,
            bib_entries=bib_entries,
            missing_bib_entries=missing_bib_entries,
            uncited_references=uncited_references,
            year_mismatches=year_mismatches
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

"""Main citation cross-checking logic."""

from typing import Optional
from .models import CheckResult, Citation, BibEntry
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
        # Parse citations from main text
        citations = self.citation_parser.parse(text)

        # Parse bibliography entries
        bib_entries, bib_text = self.bib_parser.parse(text, bib_section_name)

        # Find citations without matching bibliography entries
        missing_bib_entries = self._find_missing_bib_entries(citations, bib_entries)

        # Find bibliography entries that are never cited
        uncited_references = self._find_uncited_references(citations, bib_entries)

        return CheckResult(
            citations=citations,
            bib_entries=bib_entries,
            missing_bib_entries=missing_bib_entries,
            uncited_references=uncited_references
        )

    def check_file(
        self,
        file_path: str,
        bib_section_name: Optional[str] = None
    ) -> CheckResult:
        """
        Check a file for citation-bibliography consistency.

        Supports: .txt, .md, .docx files

        Args:
            file_path: Path to the manuscript file (.txt, .md, .docx)
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

        for citation in citations:
            # Check if this citation matches any bibliography entry
            has_match = False
            for bib_entry in bib_entries:
                if citation.matches_bib(bib_entry):
                    has_match = True
                    break

            if not has_match:
                missing.append(citation)

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

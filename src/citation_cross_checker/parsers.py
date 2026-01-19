"""Parsers for citations and bibliography entries."""

import re
from typing import List, Tuple
from .models import Citation, BibEntry


class CitationParser:
    """Parses in-text citations from manuscript text."""

    # APA style: (Author, Year) or (Author et al., Year)
    APA_PATTERN = r'\(([A-Z][a-zA-Z\s&,]+(?:\set\sal\.)?),\s*(\d{4}[a-z]?)\)'

    # MLA style: (Author Page) or (Author et al. Page)
    MLA_PATTERN = r'\(([A-Z][a-zA-Z\s&]+(?:\set\sal\.)?)\s+(\d+(?:-\d+)?)\)'

    # Numeric/IEEE: [1], [1-3], [1,2,3]
    NUMERIC_PATTERN = r'\[(\d+(?:\s*[-,]\s*\d+)*)\]'

    def parse(self, text: str) -> List[Citation]:
        """Parse all citations from text."""
        citations = []

        # Parse APA citations
        for match in re.finditer(self.APA_PATTERN, text):
            authors_str = match.group(1).strip()
            year = match.group(2).strip()
            authors = self._parse_authors(authors_str)

            citation = Citation(
                raw_text=match.group(0),
                authors=authors,
                year=year,
                position=match.start(),
                citation_type="apa"
            )
            citations.append(citation)

        # Parse MLA citations
        for match in re.finditer(self.MLA_PATTERN, text):
            authors_str = match.group(1).strip()
            page = match.group(2).strip()
            authors = self._parse_authors(authors_str)

            citation = Citation(
                raw_text=match.group(0),
                authors=authors,
                page=page,
                position=match.start(),
                citation_type="mla"
            )
            citations.append(citation)

        # Parse numeric citations
        for match in re.finditer(self.NUMERIC_PATTERN, text):
            numbers_str = match.group(1)
            # Handle ranges and lists: [1-3] or [1,2,5]
            numbers = self._parse_numbers(numbers_str)

            for num in numbers:
                citation = Citation(
                    raw_text=f"[{num}]",
                    authors=[],
                    number=num,
                    position=match.start(),
                    citation_type="numeric"
                )
                citations.append(citation)

        return citations

    def _parse_authors(self, authors_str: str) -> List[str]:
        """Parse author names from citation."""
        # Remove "et al." and split by common separators
        authors_str = authors_str.replace('et al.', '').strip()

        if '&' in authors_str:
            authors = [a.strip() for a in authors_str.split('&')]
        elif ',' in authors_str:
            authors = [a.strip() for a in authors_str.split(',')]
        else:
            authors = [authors_str.strip()]

        return [a for a in authors if a]

    def _parse_numbers(self, numbers_str: str) -> List[int]:
        """Parse numeric citations like '1-3' or '1,2,5'."""
        numbers = []

        # Handle ranges: 1-3
        if '-' in numbers_str:
            parts = numbers_str.split('-')
            if len(parts) == 2:
                try:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    numbers.extend(range(start, end + 1))
                except ValueError:
                    pass
        # Handle lists: 1,2,5
        elif ',' in numbers_str:
            for num_str in numbers_str.split(','):
                try:
                    numbers.append(int(num_str.strip()))
                except ValueError:
                    pass
        # Single number
        else:
            try:
                numbers.append(int(numbers_str.strip()))
            except ValueError:
                pass

        return numbers


class BibliographyParser:
    """Parses bibliography entries from reference section."""

    def __init__(self):
        # Common bibliography section headers
        self.bib_headers = [
            'references', 'bibliography', 'works cited', 'citations',
            'literature cited', 'sources'
        ]

    def parse(self, text: str, bib_section_name: str = None) -> Tuple[List[BibEntry], str]:
        """
        Parse bibliography entries from text.

        Returns:
            Tuple of (list of BibEntry objects, bibliography section text)
        """
        # Find bibliography section
        bib_text = self._extract_bibliography_section(text, bib_section_name)

        if not bib_text:
            return [], ""

        entries = []

        # Try to parse as numbered references first
        numbered_entries = self._parse_numbered_entries(bib_text)
        if numbered_entries:
            return numbered_entries, bib_text

        # Parse as author-year entries (APA/MLA)
        entries = self._parse_author_year_entries(bib_text)

        return entries, bib_text

    def _extract_bibliography_section(self, text: str, custom_header: str = None) -> str:
        """Extract the bibliography section from the document."""
        headers = [custom_header] if custom_header else self.bib_headers

        for header in headers:
            if not header:
                continue

            # Look for the header (case-insensitive)
            pattern = r'^' + re.escape(header) + r'\s*:?\s*$'
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)

            if match:
                # Return everything after the header
                return text[match.end():].strip()

        return ""

    def _parse_numbered_entries(self, bib_text: str) -> List[BibEntry]:
        """Parse numbered bibliography entries like [1] Author..."""
        entries = []
        # Pattern for numbered entries: [1] Author, "Title", ...
        pattern = r'^\[(\d+)\]\s*(.+?)(?=^\[\d+\]|\Z)'

        matches = list(re.finditer(pattern, bib_text, re.MULTILINE | re.DOTALL))

        if not matches:
            return []

        for match in matches:
            number = int(match.group(1))
            entry_text = match.group(2).strip()

            # Try to extract author and year
            authors, year = self._extract_author_year(entry_text)

            entry = BibEntry(
                raw_text=f"[{number}] {entry_text}",
                authors=authors,
                year=year,
                number=number,
                position=match.start(),
                entry_type="numeric"
            )
            entries.append(entry)

        return entries

    def _parse_author_year_entries(self, bib_text: str) -> List[BibEntry]:
        """Parse author-year bibliography entries (APA/MLA style)."""
        entries = []

        # Split by lines that start with a capital letter (new entry)
        lines = bib_text.split('\n')
        current_entry = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # New entry starts with capital letter or is indented differently
            if line and line[0].isupper() and current_entry:
                # Process previous entry
                entry = self._create_author_year_entry('\n'.join(current_entry))
                if entry:
                    entries.append(entry)
                current_entry = [line]
            else:
                current_entry.append(line)

        # Process last entry
        if current_entry:
            entry = self._create_author_year_entry('\n'.join(current_entry))
            if entry:
                entries.append(entry)

        return entries

    def _create_author_year_entry(self, entry_text: str) -> BibEntry:
        """Create a BibEntry from author-year formatted text."""
        authors, year = self._extract_author_year(entry_text)

        if not authors:
            return None

        # Determine if APA or MLA based on format
        entry_type = "apa" if re.search(r'\(\d{4}\)', entry_text) else "mla"

        return BibEntry(
            raw_text=entry_text,
            authors=authors,
            year=year,
            entry_type=entry_type,
            position=0
        )

    def _extract_author_year(self, text: str) -> Tuple[List[str], str]:
        """Extract author names and year from bibliography entry."""
        authors = []
        year = None

        # Extract year - look for (YYYY) or just YYYY
        year_match = re.search(r'\((\d{4}[a-z]?)\)|(?:^|\s)(\d{4}[a-z]?)(?:\.|,|\s)', text)
        if year_match:
            year = year_match.group(1) or year_match.group(2)

        # Extract authors from beginning of entry
        # Common patterns: "LastName, F." or "LastName, FirstName"
        author_pattern = r'^([A-Z][a-zA-Z\s\'-]+(?:,\s*[A-Z]\.?)?(?:\s*,?\s*&?\s*[A-Z][a-zA-Z\s\'-]+(?:,\s*[A-Z]\.?)?)*)'
        author_match = re.search(author_pattern, text)

        if author_match:
            authors_str = author_match.group(1)
            # Split by common separators
            if '&' in authors_str:
                authors = [a.strip() for a in re.split(r'\s*&\s*', authors_str)]
            elif ',' in authors_str:
                # Handle "Last, F., Last2, F2." format
                parts = authors_str.split(',')
                current_author = []
                for part in parts:
                    part = part.strip()
                    if len(part) <= 3 and '.' in part:  # Initials
                        current_author.append(part)
                        authors.append(' '.join(current_author))
                        current_author = []
                    else:
                        if current_author:
                            authors.append(' '.join(current_author))
                        current_author = [part]
                if current_author:
                    authors.append(' '.join(current_author))
            else:
                authors = [authors_str.strip()]

        return authors, year

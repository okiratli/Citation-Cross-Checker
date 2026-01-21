"""Parsers for citations and bibliography entries."""

import re
from typing import List, Tuple
from .models import Citation, BibEntry


class CitationParser:
    """Parses in-text citations from manuscript text."""

    # Author-year styles: APA, Harvard, Chicago
    # Patterns: (Author, Year), (Author Year), (Author et al., Year)
    # Unicode-aware: includes extended Latin characters (e.g., Ç, Ğ, İ, Ş for Turkish names)
    AUTHOR_YEAR_PATTERN = r'\(([A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\s&,]+(?:\set\sal\.)?),\s*(\d{4}[a-z]?)\)'

    # MLA style: (Author Page) or (Author et al. Page)
    MLA_PATTERN = r'\(([A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\s&]+(?:\set\sal\.)?)\s+(\d+(?:-\d+)?)\)'

    # Numeric/IEEE: [1], [1-3], [1,2,3]
    NUMERIC_PATTERN = r'\[(\d+(?:\s*[-,]\s*\d+)*)\]'

    def parse(self, text: str) -> List[Citation]:
        """Parse all citations from text."""
        citations = []
        parsed_positions = set()  # Track positions to avoid duplicates

        # Parse author-year citations (APA, Harvard, Chicago)
        # Including multiple citations in one set of parentheses
        # Patterns: (Author, Year), (Author Year), (Author1, Year1; Author2, Year2)
        multi_cite_pattern = r'\(([^()]+)\)'
        for match in re.finditer(multi_cite_pattern, text):
            content = match.group(1)
            # Check if this looks like citation(s)
            if re.search(r'\d{4}', content):  # Has a year
                # Split by semicolon OR by comma after year (for comma-separated multi-citations)
                # Pattern: "Author1 Year1, Author2 Year2" or "Author1 Year1; Author2 Year2"
                # Use regex to split after year when followed by comma and capital letter
                parts = []
                if ';' in content:
                    # Traditional semicolon-separated
                    parts = content.split(';')
                else:
                    # Try to split by comma after year (e.g., "2024, Gidron")
                    # Split pattern: YYYY[a-z]?,\s+[A-Z] (Unicode-aware for international names)
                    split_pattern = r'(\d{4}[a-z]?),\s+(?=[A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F])'
                    parts_raw = re.split(split_pattern, content)
                    # Reassemble: parts_raw looks like ["Author1", "2024", "Author2 Year2"]
                    # We need to combine them back: ["Author1 2024", "Author2 Year2"]
                    i = 0
                    while i < len(parts_raw):
                        if i + 1 < len(parts_raw) and re.match(r'\d{4}[a-z]?$', parts_raw[i + 1]):
                            # Combine current part with next (year)
                            parts.append(parts_raw[i] + ' ' + parts_raw[i + 1])
                            i += 2
                        else:
                            parts.append(parts_raw[i])
                            i += 1

                for part in parts:
                    part = part.strip()
                    if not part:
                        continue
                    # Extract author and year from each part
                    # Comma is optional to support both APA (Author, Year) and Harvard/Chicago (Author Year)
                    # Unicode-aware: includes extended Latin characters
                    cite_match = re.search(r'([A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\s&,]+(?:\set\sal\.)?),?\s*(\d{4}[a-z]?)', part)
                    if cite_match:
                        authors_str = cite_match.group(1).strip()
                        year = cite_match.group(2).strip()

                        # Filter out non-author patterns (like "Hypothesis", "Table", "Figure")
                        if self._is_non_author_pattern(authors_str):
                            continue

                        authors = self._parse_authors(authors_str)

                        citation = Citation(
                            raw_text=f"({part})",
                            authors=authors,
                            year=year,
                            position=match.start(),
                            citation_type="author-year"
                        )
                        citations.append(citation)
                        parsed_positions.add((match.start(), match.end()))

        # Parse narrative citations (Author (Year))
        # Used in APA, Harvard, and Chicago styles
        # Pattern: "Brown (2018)", "Smith and Jones (2020)", "Gidron, Adams, and Horne (2019)", or "Smith et al. (2020)"
        # Handles 1+ authors with commas, "and", or "&" as separators, plus optional "et al."
        # Unicode-aware: includes extended Latin characters
        # Negative lookbehind (?<!,\s) prevents matching authors in middle of comma-separated lists
        narrative_pattern = r'(?<!,\s)([A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\'\-]+(?:(?:,\s+(?:and\s+|&\s+)?|\s+(?:and|&)\s+)[A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\'\-]+)*)(?:\s+et\s+al\.?)?\s+\((\d{4}[a-z]?)\)'
        for match in re.finditer(narrative_pattern, text):
            # Skip if already parsed
            if any(start <= match.start() < end for start, end in parsed_positions):
                continue

            authors_str = match.group(1).strip()
            year = match.group(2).strip()

            # Filter out non-author patterns
            if self._is_non_author_pattern(authors_str):
                continue

            authors = self._parse_authors(authors_str)

            citation = Citation(
                raw_text=match.group(0),
                authors=authors,
                year=year,
                position=match.start(),
                citation_type="author-year"
            )
            citations.append(citation)
            parsed_positions.add((match.start(), match.end()))

        # Parse bare citations (Author Year) without parentheses
        # Common in endnotes/footnotes: "Smith 2020" or "Smith and Jones 2020"
        # IMPORTANT: Only apply this pattern within Endnotes/Footnotes sections to avoid false positives
        # in main text like "November 2002", "Around 2011", "Report 2024"

        # Find endnotes/footnotes sections
        notes_sections = []
        for header in ['Endnotes:', 'Footnotes:', 'Notes:']:
            header_pos = text.find(header)
            if header_pos != -1:
                # Find where this section ends (next major section or end of document)
                section_start = header_pos + len(header)
                # Look for next major section (References, Bibliography, etc.)
                next_section = re.search(
                    r'\n(References|Bibliography|Works Cited|Acknowledgments?|Appendix)\s*:?\s*\n',
                    text[section_start:],
                    re.IGNORECASE
                )
                if next_section:
                    section_end = section_start + next_section.start()
                else:
                    section_end = len(text)
                notes_sections.append((section_start, section_end))

        # Only parse bare citations if we found notes sections
        if notes_sections:
            bare_citation_pattern = r'([A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\'\-]+(?:(?:,\s+(?:and\s+|&\s+)?|\s+(?:and|&)\s+)[A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\'\-]+)*)(?:\s+et\s+al\.?)?\s+(\d{4}[a-z]?)(?=[\.;,:\s]|$)'
            for match in re.finditer(bare_citation_pattern, text):
                # Skip if already parsed
                if any(start <= match.start() < end for start, end in parsed_positions):
                    continue

                # CRITICAL: Only match if within a notes section
                in_notes_section = any(start <= match.start() < end for start, end in notes_sections)
                if not in_notes_section:
                    continue

                authors_str = match.group(1).strip()
                year = match.group(2).strip()

                # Filter out non-author patterns (months, common words, etc.)
                if self._is_non_author_pattern(authors_str):
                    continue

                # Additional check: skip if this looks like it's in a bibliography entry
                # Bibliography entries typically have format: "LastName, FirstName. Year."
                # Check for comma between first and second word
                start_pos = max(0, match.start() - 50)
                context_before = text[start_pos:match.start()]

                # Skip if preceded by a comma and initial (bibliography format: "Smith, J. 2020")
                if re.search(r',\s+[A-Z]\.\s*$', context_before):
                    continue

                authors = self._parse_authors(authors_str)

                # Build raw text including the matched year and terminating punctuation if present
                raw_end = match.end()
                if raw_end < len(text) and text[raw_end] in '.;,:':
                    raw_text = text[match.start():raw_end + 1].rstrip('.,;:')
                else:
                    raw_text = match.group(0)

                citation = Citation(
                    raw_text=raw_text,
                    authors=authors,
                    year=year,
                    position=match.start(),
                    citation_type="author-year"
                )
                citations.append(citation)
                parsed_positions.add((match.start(), match.end()))

        # Parse MLA citations - only if not already parsed as author-year
        for match in re.finditer(self.MLA_PATTERN, text):
            # Skip if already parsed
            if any(start <= match.start() < end for start, end in parsed_positions):
                continue

            authors_str = match.group(1).strip()
            page = match.group(2).strip()

            # Skip if the "page" is actually a 4-digit year
            if len(page) == 4 and page.isdigit():
                continue

            # Filter out non-author patterns (like "Hypothesis", "Table")
            if self._is_non_author_pattern(authors_str):
                continue

            authors = self._parse_authors(authors_str)

            citation = Citation(
                raw_text=match.group(0),
                authors=authors,
                page=page,
                position=match.start(),
                citation_type="mla"
            )
            citations.append(citation)
            parsed_positions.add((match.start(), match.end()))

        # Parse numeric citations
        for match in re.finditer(self.NUMERIC_PATTERN, text):
            # Skip if already parsed
            if any(start <= match.start() < end for start, end in parsed_positions):
                continue

            # Check for false positives (Table 1, Figure 1, etc.)
            # Look at text before the match
            start_pos = max(0, match.start() - 20)
            context_before = text[start_pos:match.start()].lower()

            # Skip if preceded by common false positive keywords
            false_positive_keywords = ['table', 'figure', 'fig.', 'fig', 'appendix', 'section', 'chapter']
            if any(keyword in context_before for keyword in false_positive_keywords):
                continue

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
            parsed_positions.add((match.start(), match.end()))

        return citations

    def _is_non_author_pattern(self, text: str) -> bool:
        """
        Check if text matches non-author patterns that shouldn't be parsed as citations.
        Examples: "Hypothesis 3", "Table 1", "Figure 2", "November 2002", "Report 2024"
        """
        text_lower = text.lower().strip()

        # List of common non-author words
        non_author_words = [
            # Document elements
            'hypothesis', 'table', 'figure', 'appendix', 'section',
            'chapter', 'equation', 'model', 'result', 'study',
            'example', 'case', 'scenario', 'version', 'step',
            # Months
            'january', 'february', 'march', 'april', 'may', 'june',
            'july', 'august', 'september', 'october', 'november', 'december',
            # Common words that appear before years
            'around', 'circa', 'before', 'after', 'since', 'until',
            'between', 'from', 'during', 'report', 'year', 'period',
            'spring', 'summer', 'fall', 'autumn', 'winter', 'quarter',
            # Other false positives
            'vol', 'volume', 'issue', 'page', 'number', 'article'
        ]

        # Check if the text starts with any non-author word
        for word in non_author_words:
            if text_lower.startswith(word):
                return True

        return False

    def _strip_citation_prefixes(self, text: str) -> str:
        """
        Remove common citation prefixes from the author string.
        Examples: "e.g., Author", "see Author", "cf. Author"
        """
        text = text.strip()

        # List of common citation prefixes (case-insensitive)
        prefixes = [
            'e.g.,', 'e.g.', 'eg.',
            'i.e.,', 'i.e.', 'ie.',
            'cf.', 'cf',
            'see', 'see also',
            'but see', 'but cf.',
            'contra',
            'compare',
        ]

        text_lower = text.lower()
        for prefix in prefixes:
            if text_lower.startswith(prefix):
                # Remove the prefix and any following whitespace
                text = text[len(prefix):].strip()
                break

        return text

    def _parse_authors(self, authors_str: str) -> List[str]:
        """Parse author names from citation."""
        # Remove citation prefixes (e.g., "e.g.,", "see", "cf.")
        authors_str = self._strip_citation_prefixes(authors_str)

        # Remove "et al." and split by common separators
        authors_str = authors_str.replace('et al.', '').strip()

        # Handle three+ author case: "Author1, Author2, and Author3"
        # Check if we have both commas and "and" (or "&")
        has_and = '&' in authors_str or re.search(r'\s+and\s+', authors_str)
        has_comma = ',' in authors_str

        if has_comma and has_and:
            # Three or more authors with format: "Author1, Author2, and Author3"
            # Replace "and" or "&" with comma for uniform splitting
            authors_str = re.sub(r'\s*&\s*|\s+and\s+', ',', authors_str)
            authors = [a.strip() for a in authors_str.split(',')]
        elif has_and:
            # Two authors: "Author1 and Author2" or "Author1 & Author2"
            authors = re.split(r'\s*&\s*|\s+and\s+', authors_str)
            authors = [a.strip() for a in authors]
        elif has_comma:
            # Split by comma (less common in citations, but handle it)
            authors = [a.strip() for a in authors_str.split(',')]
        else:
            # Single author
            authors = [authors_str.strip()]

        # Clean up each author name - remove trailing punctuation
        authors = [a.rstrip(',.;:') for a in authors]

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
        # Endnotes headers (not bibliography, but contain citations)
        self.endnotes_headers = ['notes', 'endnotes', 'footnotes']

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

        # Try to parse numbered references
        numbered_entries = self._parse_numbered_entries(bib_text)

        # Try to parse author-year entries
        author_year_entries = self._parse_author_year_entries(bib_text)

        # Combine both types (some bibliographies have mixed formats)
        entries = numbered_entries + author_year_entries

        # If no entries found at all, return empty
        if not entries:
            return [], bib_text

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
                # Find the next section header (if any) to limit the bibliography section
                # This prevents including endnotes in the bibliography
                bib_start = match.end()

                # Look for next major section after bibliography
                # Include Notes/Endnotes/Footnotes to prevent them from being part of bibliography
                next_section = re.search(
                    r'^(acknowledgments?|appendix|supplementary materials?|notes|endnotes|footnotes)\s*:?\s*$',
                    text[bib_start:],
                    re.MULTILINE | re.IGNORECASE
                )

                if next_section:
                    return text[bib_start:bib_start + next_section.start()].strip()
                else:
                    return text[bib_start:].strip()

        return ""

    def extract_endnotes_section(self, text: str) -> str:
        """
        Extract the endnotes/notes section from the document.
        This section often contains citations that should be parsed.
        """
        for header in self.endnotes_headers:
            # Look for the header (case-insensitive)
            pattern = r'^' + re.escape(header) + r'\s*:?\s*$'
            match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)

            if match:
                # Find where this section ends (before References/Bibliography)
                notes_start = match.end()

                # Look for bibliography section that follows
                for bib_header in self.bib_headers:
                    bib_pattern = r'^' + re.escape(bib_header) + r'\s*:?\s*$'
                    bib_match = re.search(bib_pattern, text[notes_start:], re.MULTILINE | re.IGNORECASE)

                    if bib_match:
                        return text[notes_start:notes_start + bib_match.start()].strip()

                # If no bibliography found after, return rest of document
                return text[notes_start:].strip()

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

        # Split by lines - detect new entries by pattern matching
        lines = bib_text.split('\n')
        current_entry = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this line starts a new bibliography entry
            # Typical patterns: "LastName, FirstName" or "LastName, F."
            # Look for: Capital letter, followed by letters, then comma, then space, then capital letter
            # Unicode-aware: includes extended Latin characters
            is_new_entry = re.match(r'^[A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F][a-zA-Z\u00C0-\u024F\'\-]+,\s+[A-Z\u00C0-\u00D6\u00D8-\u00DE\u0100-\u024F]', line)

            if is_new_entry and current_entry:
                # Process previous entry
                entry = self._create_author_year_entry(' '.join(current_entry))
                if entry:
                    entries.append(entry)
                current_entry = [line]
            else:
                current_entry.append(line)

        # Process last entry
        if current_entry:
            entry = self._create_author_year_entry(' '.join(current_entry))
            if entry:
                entries.append(entry)

        return entries

    def _create_author_year_entry(self, entry_text: str) -> BibEntry:
        """Create a BibEntry from author-year formatted text."""
        authors, year = self._extract_author_year(entry_text)

        if not authors:
            return None

        # Determine if author-year (APA/Harvard/Chicago) or MLA based on format
        entry_type = "author-year" if re.search(r'\(\d{4}\)', entry_text) else "mla"

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

        # Extract authors - handle different bibliography formats
        # Common formats:
        # 1. "LastName, FirstName (Year)..."
        # 2. "LastName, F. M. (Year)..."
        # 3. "LastName, F., LastName2, F., & LastName3, F. (Year)..."

        # Find everything before the year (if year exists)
        if year and f'({year})' in text:
            # APA style with (Year)
            before_year = text.split(f'({year})')[0].strip()
        elif year and year in text:
            # Try to find text before year
            year_pos = text.find(year)
            before_year = text[:year_pos].strip()
            # Remove trailing punctuation
            before_year = before_year.rstrip('.,() ')
        else:
            # No year found, try to extract from beginning until period or title
            # Look for text before a period followed by uppercase (likely title)
            period_match = re.search(r'^([^.]+?)\.(?:\s+[A-Z]|$)', text)
            if period_match:
                before_year = period_match.group(1).strip()
            else:
                # Just take everything before any quote marks or title indicators
                quote_match = re.search(r'^([^"\']+)', text)
                if quote_match:
                    before_year = quote_match.group(1).strip()
                else:
                    before_year = text[:100]  # Fallback

        # Remove "et al." from bibliography entries (e.g., "Türkoğlu, D. et al. (2022)")
        # This should be removed before parsing author names
        before_year = before_year.replace('et al.', '').replace('et al', '').strip()

        # Now parse authors from this section
        # Split by '&' or 'and' first (for multiple authors)
        author_parts = re.split(r'\s+&\s+|\s+and\s+', before_year)

        for author_part in author_parts:
            author_part = author_part.strip()
            if not author_part:
                continue

            # For each author part, extract the last name
            # Format: "LastName, FirstName" or "LastName, F. M." or just "LastName"
            # OR mixed: "LastName, FirstName, FirstName LastName, FirstName LastName"
            if ',' in author_part:
                # Split by ALL commas to handle mixed formats
                # Example: "Tomz, Michael, Jessica LP Weeks" -> ["Tomz", "Michael", "Jessica LP Weeks"]
                comma_parts = author_part.split(',')
                for i, comma_part in enumerate(comma_parts):
                    comma_part = comma_part.strip()
                    if not comma_part:
                        continue

                    if i == 0:
                        # First part is always the first author's last name
                        authors.append(comma_part)
                    else:
                        # Check if this is a subsequent author (FirstName LastName)
                        # or just the first author's first name/initials
                        words = comma_part.split()
                        real_words = [w for w in words if len(w.replace('.', '')) > 1]

                        if len(real_words) >= 2:
                            # Multiple words - this is a subsequent author in "FirstName LastName" format
                            # Extract last word as last name
                            authors.append(real_words[-1])
                        elif len(real_words) == 1 and len(real_words[0]) > 2:
                            # Single word but long enough to be a last name (not just initials)
                            # E.g., "Gentzkow" in "Boxell, L., Gentzkow, M."
                            authors.append(real_words[0])
                        # else: Just initials - skip (likely first author's first name)
            else:
                # No comma, might be "FirstName LastName" format or just "LastName"
                # Take the last word as the last name
                words = author_part.strip().split()
                if words:
                    # Filter out initials (single letters with periods)
                    real_words = [w for w in words if len(w.replace('.', '')) > 1]
                    if real_words:
                        authors.append(real_words[-1])
                    elif words:
                        authors.append(words[-1])

        # Clean up authors list - remove empty strings and duplicates while preserving order
        seen = set()
        authors = [a for a in authors if a and a not in seen and not seen.add(a)]

        return authors, year

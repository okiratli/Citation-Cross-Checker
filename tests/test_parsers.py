"""Tests for citation and bibliography parsers."""

import pytest
from citation_cross_checker.parsers import CitationParser, BibliographyParser


class TestCitationParser:
    """Test citation parsing."""

    def test_parse_apa_citations(self):
        """Test parsing APA style citations."""
        parser = CitationParser()
        text = "Recent research (Smith, 2020) shows results. Others agree (Jones et al., 2021)."

        citations = parser.parse(text)

        assert len(citations) == 2
        assert citations[0].raw_text == "(Smith, 2020)"
        assert citations[0].authors == ["Smith"]
        assert citations[0].year == "2020"
        assert citations[0].citation_type == "apa"

        assert citations[1].raw_text == "(Jones et al., 2021)"
        assert "Jones" in citations[1].authors
        assert citations[1].year == "2021"

    def test_parse_mla_citations(self):
        """Test parsing MLA style citations."""
        parser = CitationParser()
        text = "As stated (Author 123) and confirmed (Writer et al. 45-67)."

        citations = parser.parse(text)

        assert len(citations) == 2
        assert citations[0].raw_text == "(Author 123)"
        assert citations[0].authors == ["Author"]
        assert citations[0].page == "123"
        assert citations[0].citation_type == "mla"

    def test_parse_numeric_citations(self):
        """Test parsing numeric/IEEE style citations."""
        parser = CitationParser()
        text = "Research shows [1] that citations matter [2,3,5] and ranges work [10-12]."

        citations = parser.parse(text)

        # Should find: [1], [2], [3], [5], [10], [11], [12]
        assert len(citations) >= 7
        numbers = [c.number for c in citations if c.citation_type == "numeric"]
        assert 1 in numbers
        assert 2 in numbers
        assert 3 in numbers
        assert 5 in numbers
        assert 10 in numbers
        assert 11 in numbers
        assert 12 in numbers

    def test_parse_mixed_citations(self):
        """Test parsing document with mixed citation styles."""
        parser = CitationParser()
        text = "Some use APA (Smith, 2020) while others use numeric [1]."

        citations = parser.parse(text)

        assert len(citations) == 2
        apa_citations = [c for c in citations if c.citation_type == "apa"]
        numeric_citations = [c for c in citations if c.citation_type == "numeric"]
        assert len(apa_citations) == 1
        assert len(numeric_citations) == 1


class TestBibliographyParser:
    """Test bibliography parsing."""

    def test_parse_apa_bibliography(self):
        """Test parsing APA style bibliography."""
        parser = BibliographyParser()
        text = """
Some intro text here.

References:
Smith, J. (2020). A Study on Citations. Journal of Research, 15(2), 120-135.
Jones, M., Lee, K., & Chen, R. (2021). Advanced Methods. Science Press.
Williams, A. (2019). Research Methodology. Academic Publishers.
"""

        entries, bib_text = parser.parse(text)

        assert len(entries) == 3
        assert entries[0].authors[0].startswith("Smith")
        assert entries[0].year == "2020"
        assert entries[1].year == "2021"
        assert entries[2].year == "2019"

    def test_parse_numeric_bibliography(self):
        """Test parsing numeric bibliography."""
        parser = BibliographyParser()
        text = """
Introduction text.

References:
[1] J. Smith, "Title of Paper," Journal Name, vol. 1, pp. 1-10, 2020.
[2] M. Jones and K. Lee, "Another Paper," Conference, 2021.
[3] A. Williams, "Third Paper," Publisher, 2019.
"""

        entries, bib_text = parser.parse(text)

        assert len(entries) == 3
        assert entries[0].number == 1
        assert entries[1].number == 2
        assert entries[2].number == 3
        assert entries[0].entry_type == "numeric"

    def test_custom_bibliography_header(self):
        """Test parsing with custom bibliography section name."""
        parser = BibliographyParser()
        text = """
Document text.

Works Cited:
Smith, J. (2020). A Study. Publisher.
"""

        entries, bib_text = parser.parse(text, "Works Cited")

        assert len(entries) == 1
        assert "Smith" in entries[0].authors[0]

    def test_no_bibliography_found(self):
        """Test when no bibliography section is found."""
        parser = BibliographyParser()
        text = "Just some text without a bibliography section."

        entries, bib_text = parser.parse(text)

        assert len(entries) == 0
        assert bib_text == ""

"""Tests for improved author name parsing."""

import pytest
from citation_cross_checker.parsers import BibliographyParser
from citation_cross_checker.checker import CitationChecker


class TestAuthorNameParsing:
    """Test that author names are correctly extracted from bibliography."""

    def test_lastname_firstname_format(self):
        """Test parsing 'LastName, FirstName' format."""
        parser = BibliographyParser()

        text = """
References:
Smith, John (2020). Article Title. Journal Name.
Johnson, Mary Ann (2021). Another Article. Publisher.
"""

        entries, _ = parser.parse(text)

        assert len(entries) == 2
        assert entries[0].authors == ["Smith"]
        assert entries[0].year == "2020"
        assert entries[1].authors == ["Johnson"]
        assert entries[1].year == "2021"

    def test_lastname_initials_format(self):
        """Test parsing 'LastName, F. M.' format."""
        parser = BibliographyParser()

        text = """
References:
Williams, A. B. (2019). Title Here. Press.
Garcia, P. (2022). Another Work. Publisher.
"""

        entries, _ = parser.parse(text)

        assert len(entries) == 2
        assert "Williams" in entries[0].authors
        assert "Garcia" in entries[1].authors

    def test_multiple_authors_ampersand(self):
        """Test parsing multiple authors with '&'."""
        parser = BibliographyParser()

        text = """
References:
Taylor, R., & Martinez, L. (2020). Joint Work. Press.
"""

        entries, _ = parser.parse(text)

        assert len(entries) == 1
        assert "Taylor" in entries[0].authors
        assert "Martinez" in entries[0].authors

    def test_matching_with_lastname_firstname(self):
        """Test that citations match bibliography with LastName, FirstName format."""
        checker = CitationChecker()

        text = """
Recent research shows important findings (Smith, 2020). Other work
confirms this (Johnson, 2021).

References:
Smith, John Michael (2020). Important Findings. Journal of Research.
Johnson, Mary Ann (2021). Confirmatory Study. Science Publishers.
"""

        result = checker.check_document(text)

        # Should have no issues - both citations should match bibliography
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_et_al_with_multiple_authors(self):
        """Test that 'et al.' citations match multi-author bibliography."""
        checker = CitationChecker()

        text = """
Previous work (Taylor et al., 2020) established the framework.

References:
Taylor, Robert, & Martinez, Linda (2020). Framework Establishment. Press.
"""

        result = checker.check_document(text)

        # Should match because first author is Taylor
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_three_authors_format(self):
        """Test parsing three authors."""
        parser = BibliographyParser()

        text = """
References:
Smith, J., Jones, M., & Lee, K. (2020). Collaborative Work. Publisher.
"""

        entries, _ = parser.parse(text)

        assert len(entries) == 1
        assert "Smith" in entries[0].authors
        assert "Jones" in entries[0].authors
        assert "Lee" in entries[0].authors

    def test_no_false_uncited_warnings(self):
        """Test that properly cited references don't get flagged as uncited."""
        checker = CitationChecker()

        text = """
Research by Brown (2018) and Davis (2019) shows consensus. Additional
support comes from Wilson (2020) and Chen (2021).

References:
Brown, Thomas A. (2018). First Study. University Press.
Davis, Karen Marie (2019). Second Study. Academic Publishers.
Wilson, Robert (2020). Third Study. Science Press.
Chen, Li (2021). Fourth Study. Research Publishers.
"""

        result = checker.check_document(text)

        # All references are cited - should have no uncited references
        assert len(result.uncited_references) == 0
        # All citations have entries - should have no missing entries
        assert len(result.missing_bib_entries) == 0

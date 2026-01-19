"""Tests for deduplication and Harvard/Chicago citation styles."""

from citation_cross_checker.checker import CitationChecker


class TestDeduplication:
    """Test that duplicate citations are not reported multiple times."""

    def test_duplicate_citations_not_reported_twice(self):
        """Test that same citation appearing multiple times is only reported once."""
        checker = CitationChecker()

        text = """
Research by Smith (2020) is important. Later, Smith (2020) confirms this.
Additional work by Smith (2020) provides more evidence. Smith (2020) is key.

References:
Jones, Mary. 2021. "Different Work." Journal Name 1(1): 1-10.
"""

        result = checker.check_document(text)

        # Should find 4 citation instances but only report Smith 2020 once as missing
        assert len(result.citations) == 4
        assert len(result.missing_bib_entries) == 1
        assert result.missing_bib_entries[0].year == '2020'
        assert 'Smith' in result.missing_bib_entries[0].authors

    def test_multiple_different_missing_citations(self):
        """Test that different missing citations are all reported."""
        checker = CitationChecker()

        text = """
Work by Smith (2020), Jones (2021), and Brown (2019) is important.
Smith (2020) and Jones (2021) agree.

References:
Williams, Sarah. 2018. "Different Work." Journal 1(1): 1-10.
"""

        result = checker.check_document(text)

        # Should report each unique missing citation once
        assert len(result.missing_bib_entries) == 3
        missing_keys = {(c.authors[0], c.year) for c in result.missing_bib_entries}
        assert ('Smith', '2020') in missing_keys
        assert ('Jones', '2021') in missing_keys
        assert ('Brown', '2019') in missing_keys


class TestHarvardStyle:
    """Test Harvard citation style support."""

    def test_harvard_parenthetical_citations(self):
        """Test Harvard style (Author Year) without comma."""
        checker = CitationChecker()

        text = """
Research shows (Smith 2020) and (Jones 2021) important findings.

References:
Smith, John A. 2020. "Important Research." Journal Name 15(3): 123-145.
Jones, Mary K. 2021. "Additional Work." Science Review 8(2): 56-78.
"""

        result = checker.check_document(text)

        assert len(result.citations) == 2
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_harvard_with_comma_also_works(self):
        """Test that Harvard also accepts (Author, Year) with comma."""
        checker = CitationChecker()

        text = """
Research (Smith, 2020) shows findings.

References:
Smith, John A. 2020. "Research." Journal 15(3): 123-145.
"""

        result = checker.check_document(text)

        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_harvard_narrative_citations(self):
        """Test Harvard narrative citations Author (Year)."""
        checker = CitationChecker()

        text = """
As Smith (2020) demonstrates, the method works.

References:
Smith, John A. 2020. "Methodology." Journal 10(1): 34-56.
"""

        result = checker.check_document(text)

        assert len(result.citations) == 1
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0


class TestChicagoStyle:
    """Test Chicago author-date citation style support."""

    def test_chicago_parenthetical_citations(self):
        """Test Chicago style (Author Year)."""
        checker = CitationChecker()

        text = """
Research (Brown 2019) and (Taylor 2021) shows results.

References:
Brown, Thomas. 2019. "Research Methods." Journal 10(1): 34-56.
Taylor, Sarah. 2021. "Results Analysis." Review 5(2): 78-90.
"""

        result = checker.check_document(text)

        assert len(result.citations) == 2
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_chicago_narrative_citations(self):
        """Test Chicago narrative citations."""
        checker = CitationChecker()

        text = """
As Brown (2019) demonstrates, the method works. Smith and Jones (2020) confirm this.

References:
Brown, Thomas. 2019. "Methodology." Research Journal 10(1): 34-56.
Smith, Anna, and Michael Jones. 2020. "Confirmation." Science Today 5(2): 78-90.
"""

        result = checker.check_document(text)

        assert len(result.citations) == 2
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_chicago_multiple_authors(self):
        """Test Chicago with multiple authors."""
        checker = CitationChecker()

        text = """
Research (Smith and Jones 2020) is important.

References:
Smith, Anna, and Michael Jones. 2020. "Research." Journal 5(2): 78-90.
"""

        result = checker.check_document(text)

        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0


class TestMixedStyles:
    """Test documents with mixed citation styles."""

    def test_mixed_apa_and_harvard(self):
        """Test that APA and Harvard can coexist in same document."""
        checker = CitationChecker()

        text = """
Research by Smith (2020) and work by Jones (2021) shows results.
Additional evidence (Brown, 2019) and (Williams 2018) confirms this.

References:
Smith, John. 2020. "Research." Journal 1(1): 1-10.
Jones, Mary. 2021. "Work." Journal 2(2): 20-30.
Brown, Tom. 2019. "Evidence." Journal 3(3): 40-50.
Williams, Sarah. 2018. "Confirmation." Journal 4(4): 60-70.
"""

        result = checker.check_document(text)

        # Should parse all citations correctly
        assert len(result.citations) == 5  # Note: "Smith (2020)" is narrative, "(Jones, 2021)" is parenthetical
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

"""Tests for citation checker."""

import pytest
from citation_cross_checker.checker import CitationChecker


class TestCitationChecker:
    """Test the main citation checker."""

    def test_check_document_no_issues(self):
        """Test document with all citations matching bibliography."""
        checker = CitationChecker()
        text = """
Recent studies (Smith, 2020) show important results. Multiple
researchers agree (Johnson, 2021).

References:
Smith, J. (2020). A Study on Citations. Journal of Research.
Johnson, M. (2021). Advanced Methods. Science Press.
"""

        result = checker.check_document(text)

        assert not result.has_issues()
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0
        assert len(result.citations) == 2
        assert len(result.bib_entries) == 2

    def test_check_document_missing_bib_entry(self):
        """Test document with citation but no bibliography entry."""
        checker = CitationChecker()
        text = """
Recent studies (Smith, 2020) and also (Jones, 2019).

References:
Smith, J. (2020). A Study on Citations. Journal of Research.
"""

        result = checker.check_document(text)

        assert result.has_issues()
        assert len(result.missing_bib_entries) == 1
        assert result.missing_bib_entries[0].raw_text == "(Jones, 2019)"
        assert len(result.uncited_references) == 0

    def test_check_document_uncited_reference(self):
        """Test document with bibliography entry never cited."""
        checker = CitationChecker()
        text = """
Recent studies (Smith, 2020) show results.

References:
Smith, J. (2020). A Study on Citations. Journal of Research.
Jones, M. (2021). Never Cited Work. Publisher.
Williams, A. (2019). Also Not Cited. Press.
"""

        result = checker.check_document(text)

        assert result.has_issues()
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 2

    def test_check_document_numeric_style(self):
        """Test document with numeric citations."""
        checker = CitationChecker()
        text = """
Research shows [1] that citations are important [2].

References:
[1] J. Smith, "Title," Journal, 2020.
[2] M. Jones, "Another," Conference, 2021.
[3] A. Williams, "Uncited," Publisher, 2019.
"""

        result = checker.check_document(text)

        assert result.has_issues()
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 1
        assert result.uncited_references[0].number == 3

    def test_check_document_et_al_matching(self):
        """Test that et al. citations match multi-author bibliography."""
        checker = CitationChecker()
        text = """
Research (Smith et al., 2020) is important.

References:
Smith, J., Jones, M., & Lee, K. (2020). Multi-Author Work. Publisher.
"""

        result = checker.check_document(text)

        # Should match because first author is Smith
        assert not result.has_issues()
        assert len(result.missing_bib_entries) == 0

    def test_generate_report(self):
        """Test that report generation works."""
        checker = CitationChecker()
        text = """
Citation (Smith, 2020) here.

References:
Smith, J. (2020). Work. Publisher.
"""

        result = checker.check_document(text)
        report = result.generate_report(use_colors=False)

        assert "Citation Cross-Checker Report" in report
        assert "SUMMARY" in report
        assert "ALL CHECKS PASSED" in report

    def test_empty_document(self):
        """Test empty document."""
        checker = CitationChecker()
        text = ""

        result = checker.check_document(text)

        assert not result.has_issues()
        assert len(result.citations) == 0
        assert len(result.bib_entries) == 0

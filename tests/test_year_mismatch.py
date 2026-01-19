"""Tests for year mismatch detection."""

from citation_cross_checker.checker import CitationChecker


class TestYearMismatchDetection:
    """Test year mismatch detection functionality."""

    def test_single_author_year_mismatch(self):
        """Test detecting year mismatch for single author."""
        checker = CitationChecker()

        text = """
Research shows important findings (Smith, 2023).

References:
Smith, John A. 2024. "Important Findings." Journal Name 15(3): 123-145.
"""

        result = checker.check_document(text)

        # Should detect one year mismatch
        assert len(result.year_mismatches) == 1
        assert result.year_mismatches[0].citation.year == '2023'
        assert result.year_mismatches[0].bib_entry.year == '2024'
        # Authors should match
        assert result.year_mismatches[0].citation.authors[0] == 'Smith'
        assert result.year_mismatches[0].bib_entry.authors[0] == 'Smith'

    def test_multiple_authors_year_mismatch(self):
        """Test detecting year mismatch for multiple authors."""
        checker = CitationChecker()

        text = """
Studies by Brown and Williams (2021) show results.

References:
Brown, Thomas, and Sarah Williams. 2022. "Study Results." Journal 10(1): 34-56.
"""

        result = checker.check_document(text)

        # Should detect one year mismatch
        assert len(result.year_mismatches) == 1
        assert result.year_mismatches[0].citation.year == '2021'
        assert result.year_mismatches[0].bib_entry.year == '2022'

    def test_multiple_year_mismatches(self):
        """Test detecting multiple year mismatches."""
        checker = CitationChecker()

        text = """
Research by Smith (2023) and Jones (2020) shows findings. Additional work
by Brown and Williams (2021) confirms this.

References:
Smith, John A. 2024. "Findings." Journal 15(3): 123-145.
Jones, Mary K. 2021. "Additional Work." Review 8(2): 56-78.
Brown, Thomas, and Sarah Williams. 2022. "Confirmation." Quarterly 10(1): 34-56.
"""

        result = checker.check_document(text)

        # Should detect three year mismatches
        assert len(result.year_mismatches) == 3

    def test_no_year_mismatch_when_years_match(self):
        """Test that no mismatch is detected when years match correctly."""
        checker = CitationChecker()

        text = """
Research by Smith (2024) shows findings.

References:
Smith, John A. 2024. "Findings." Journal 15(3): 123-145.
"""

        result = checker.check_document(text)

        # Should have no issues
        assert len(result.year_mismatches) == 0
        assert len(result.missing_bib_entries) == 0
        assert len(result.uncited_references) == 0

    def test_year_mismatch_in_report(self):
        """Test that year mismatches appear in the report."""
        checker = CitationChecker()

        text = """
Research shows important findings (Smith, 2023).

References:
Smith, John A. 2024. "Important Findings." Journal Name 15(3): 123-145.
"""

        result = checker.check_document(text)
        report = result.generate_report(use_colors=False)

        # Report should mention year mismatches
        assert "POTENTIAL YEAR MISMATCHES" in report
        assert "Smith, 2023" in report or "(Smith, 2023)" in report
        assert "2024" in report
        assert "Potential year mismatches: 1" in report

    def test_year_mismatch_with_et_al(self):
        """Test year mismatch detection with et al. citations."""
        checker = CitationChecker()

        text = """
Research (Smith et al., 2023) shows findings.

References:
Smith, John A., Jones, Mary, and Lee, Kevin. 2024. "Findings." Journal 15(3): 123-145.
"""

        result = checker.check_document(text)

        # Should detect year mismatch even with et al.
        assert len(result.year_mismatches) == 1
        assert result.year_mismatches[0].citation.year == '2023'
        assert result.year_mismatches[0].bib_entry.year == '2024'

    def test_no_year_mismatch_different_authors(self):
        """Test that different authors don't create false year mismatches."""
        checker = CitationChecker()

        text = """
Research by Smith (2023) and Jones (2024) shows findings.

References:
Jones, Mary K. 2024. "Findings." Journal 8(2): 56-78.
"""

        result = checker.check_document(text)

        # Should have missing entry for Smith but no year mismatch
        # (Smith and Jones are different authors)
        assert len(result.missing_bib_entries) == 1
        assert result.missing_bib_entries[0].authors == ['Smith']
        assert len(result.year_mismatches) == 0

    def test_online_first_scenario(self):
        """Test realistic online-first publication scenario."""
        checker = CitationChecker()

        text = """
The framework was established by Taylor and Martinez (2020). Subsequently,
it was refined (Garcia, 2021) and applied in practice (Chen et al., 2022).

References:
Taylor, Robert, and Linda Martinez. 2021. "Framework Establishment."
International Journal 25(4): 450-478.

Garcia, Patricia M. 2022. "Framework Refinement." Research Review 12(1): 23-45.

Chen, Li, Wang, Mei, and Kumar, Raj. 2022. "Practical Applications."
Applied Science 8(3): 156-172.
"""

        result = checker.check_document(text)

        # Should detect two year mismatches (Taylor 2020->2021, Garcia 2021->2022)
        # but not Chen (matches)
        assert len(result.year_mismatches) == 2
        # Chen should match correctly
        assert len([c for c in result.citations if 'Chen' in c.authors]) == 1

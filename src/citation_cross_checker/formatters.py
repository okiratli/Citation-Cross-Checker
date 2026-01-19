"""Output formatters for check results."""

from .models import CheckResult


class ReportFormatter:
    """Formats check results into human-readable reports."""

    def __init__(self, use_colors: bool = True):
        self.use_colors = use_colors

        # ANSI color codes
        if use_colors:
            try:
                import colorama
                colorama.init()
                self.RED = '\033[91m'
                self.GREEN = '\033[92m'
                self.YELLOW = '\033[93m'
                self.BLUE = '\033[94m'
                self.BOLD = '\033[1m'
                self.RESET = '\033[0m'
            except ImportError:
                self._disable_colors()
        else:
            self._disable_colors()

    def _disable_colors(self):
        """Disable color output."""
        self.RED = ''
        self.GREEN = ''
        self.YELLOW = ''
        self.BLUE = ''
        self.BOLD = ''
        self.RESET = ''

    def format_result(self, result: CheckResult) -> str:
        """Format a CheckResult into a report."""
        lines = []

        # Header
        lines.append(f"{self.BOLD}Citation Cross-Checker Report{self.RESET}")
        lines.append("=" * 60)
        lines.append("")

        # Missing bibliography entries
        if result.missing_bib_entries:
            lines.append(f"{self.RED}{self.BOLD}MISSING BIBLIOGRAPHY ENTRIES:{self.RESET}")
            for citation in result.missing_bib_entries:
                lines.append(f"  {self.RED}✗{self.RESET} Citation '{citation.raw_text}' found in text but missing from bibliography")
            lines.append("")
        else:
            lines.append(f"{self.GREEN}✓ All citations have bibliography entries{self.RESET}")
            lines.append("")

        # Uncited references
        if result.uncited_references:
            lines.append(f"{self.YELLOW}{self.BOLD}UNCITED REFERENCES:{self.RESET}")
            for bib_entry in result.uncited_references:
                key = bib_entry.get_key()
                lines.append(f"  {self.YELLOW}✗{self.RESET} '{key}' in bibliography but never cited in text")
            lines.append("")
        else:
            lines.append(f"{self.GREEN}✓ All bibliography entries are cited{self.RESET}")
            lines.append("")

        # Year mismatches
        if result.year_mismatches:
            lines.append(f"{self.BLUE}{self.BOLD}POTENTIAL YEAR MISMATCHES:{self.RESET}")
            lines.append(f"{self.BLUE}(Same authors cited and in bibliography, but with different years){self.RESET}")
            for mismatch in result.year_mismatches:
                citation_year = mismatch.citation.year
                bib_year = mismatch.bib_entry.year
                bib_key = mismatch.bib_entry.get_key()
                lines.append(f"  {self.BLUE}⚠{self.RESET}  Citation: {mismatch.citation.raw_text} (year: {citation_year})")
                lines.append(f"      Bibliography: {bib_key} (year: {bib_year})")
            lines.append("")

        # Summary
        lines.append(f"{self.BOLD}SUMMARY:{self.RESET}")
        lines.append(f"  Total in-text citations: {len(result.citations)}")
        lines.append(f"  Total bibliography entries: {len(result.bib_entries)}")
        lines.append(f"  Missing bibliography entries: {self.RED}{len(result.missing_bib_entries)}{self.RESET}")
        lines.append(f"  Uncited references: {self.YELLOW}{len(result.uncited_references)}{self.RESET}")
        lines.append(f"  Potential year mismatches: {self.BLUE}{len(result.year_mismatches)}{self.RESET}")
        lines.append("")

        # Status
        if result.has_issues():
            status = f"{self.RED}INCONSISTENCIES FOUND{self.RESET}"
        else:
            status = f"{self.GREEN}ALL CHECKS PASSED{self.RESET}"

        lines.append(f"Status: {status}")

        return '\n'.join(lines)

    def format_verbose(self, result: CheckResult) -> str:
        """Format a detailed verbose report."""
        lines = [self.format_result(result)]
        lines.append("")
        lines.append("=" * 60)
        lines.append(f"{self.BOLD}DETAILED INFORMATION{self.RESET}")
        lines.append("=" * 60)
        lines.append("")

        # List all citations
        lines.append(f"{self.BOLD}All Citations Found:{self.RESET}")
        if result.citations:
            for i, citation in enumerate(result.citations, 1):
                lines.append(f"  {i}. {citation.raw_text} ({citation.citation_type})")
        else:
            lines.append("  (none)")
        lines.append("")

        # List all bibliography entries
        lines.append(f"{self.BOLD}All Bibliography Entries:{self.RESET}")
        if result.bib_entries:
            for i, entry in enumerate(result.bib_entries, 1):
                key = entry.get_key()
                lines.append(f"  {i}. {key}")
        else:
            lines.append("  (none)")

        return '\n'.join(lines)

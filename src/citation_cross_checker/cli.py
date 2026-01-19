"""Command-line interface for Citation Cross-Checker."""

import sys
import click
from pathlib import Path
from .checker import CitationChecker
from .formatters import ReportFormatter


@click.group()
@click.version_option(version="1.0.0")
def main():
    """Citation Cross-Checker: Verify citations match bibliography entries."""
    pass


@main.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option(
    '--bib-section',
    '-b',
    default=None,
    help='Custom name for bibliography section (e.g., "Works Cited")'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    default=None,
    help='Save report to file instead of printing to console'
)
@click.option(
    '--verbose',
    '-v',
    is_flag=True,
    help='Show detailed information about all citations and references'
)
@click.option(
    '--no-color',
    is_flag=True,
    help='Disable colored output'
)
def check(file_path, bib_section, output, verbose, no_color):
    """Check a manuscript file for citation consistency."""
    try:
        # Initialize checker
        checker = CitationChecker()

        # Run check
        click.echo(f"Checking {file_path}...")
        result = checker.check_file(file_path, bib_section)

        # Format report
        formatter = ReportFormatter(use_colors=not no_color)
        if verbose:
            report = formatter.format_verbose(result)
        else:
            report = formatter.format_result(result)

        # Output report
        if output:
            output_path = Path(output)
            output_path.write_text(report)
            click.echo(f"Report saved to {output}")
        else:
            click.echo(report)

        # Exit with error code if issues found
        if result.has_issues():
            sys.exit(1)
        else:
            sys.exit(0)

    except FileNotFoundError:
        click.echo(f"Error: File '{file_path}' not found", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)


@main.command()
def example():
    """Show example usage and supported formats."""
    example_text = """
Citation Cross-Checker - Example Usage

SUPPORTED FORMATS:

1. APA Style
   In-text: (Smith, 2020) or (Johnson et al., 2021)
   Bibliography: Smith, J. (2020). Title of work. Publisher.

2. MLA Style
   In-text: (Author 123) or (Author et al. 45-67)
   Bibliography: Author, First. "Title of Work." Publisher, 2020.

3. IEEE/Numeric Style
   In-text: [1] or [1-3] or [1,2,5]
   Bibliography: [1] J. Smith, "Title," Journal, vol. 1, 2020.

EXAMPLE DOCUMENT:

Recent studies (Smith, 2020) show that citations are important.
Multiple researchers agree (Johnson et al., 2021; Williams, 2019).
Some findings are controversial [3].

References:
Smith, J. (2020). A Study on Citations. Journal of Research.
Johnson, M., Lee, K., & Chen, R. (2021). Advanced Methods. Science Press.
Williams, A. (2019). Research Methodology. Academic Publishers.

USAGE EXAMPLES:

  # Check a document
  citation-checker check manuscript.txt

  # Use custom bibliography section name
  citation-checker check paper.txt --bib-section "Works Cited"

  # Save report to file
  citation-checker check thesis.txt --output report.txt

  # Verbose output
  citation-checker check article.txt --verbose

  # Disable colors
  citation-checker check paper.txt --no-color
"""
    click.echo(example_text)


if __name__ == '__main__':
    main()

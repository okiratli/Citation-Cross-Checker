# Quick Start Guide

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd abc

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Basic Usage

### Check a manuscript file

Supports .txt, .md, .docx (Word) files:

```bash
citation-checker check examples/sample_manuscript.txt
```

Or check a Word document:

```bash
citation-checker check your_thesis.docx
```

### Check a file with issues

```bash
citation-checker check examples/manuscript_with_issues.txt
```

This will show:
- Citations found in text but missing from bibliography
- Bibliography entries never cited in the text
- Summary statistics

### Verbose output

```bash
citation-checker check manuscript.txt --verbose
```

Shows detailed information about all citations and bibliography entries found.

### Save report to file

```bash
citation-checker check manuscript.txt --output report.txt
```

### Custom bibliography section name

```bash
citation-checker check manuscript.txt --bib-section "Works Cited"
```

## Python API

```python
from citation_cross_checker import CitationChecker

# Create checker
checker = CitationChecker()

# Check a file
result = checker.check_file('manuscript.txt')

# Check text directly
with open('manuscript.txt', 'r') as f:
    text = f.read()
result = checker.check_document(text)

# Generate report
print(result.generate_report())

# Check for issues
if result.has_issues():
    print("Found inconsistencies!")
    print(f"Missing bibliography entries: {len(result.missing_bib_entries)}")
    print(f"Uncited references: {len(result.uncited_references)}")
```

## Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=citation_cross_checker
```

## Example Output

```
Citation Cross-Checker Report
========================================

MISSING BIBLIOGRAPHY ENTRIES:
  ✗ Citation '(Williams, 2019)' found in text but missing from bibliography
  ✗ Citation '(Garcia et al., 2022)' found in text but missing from bibliography
  ✗ Citation '[5]' found in text but missing from bibliography

UNCITED REFERENCES:
  ✗ 'Lee, K. (2017)' in bibliography but never cited in text
  ✗ 'Davis, R. (2019)' in bibliography but never cited in text

SUMMARY:
  Total in-text citations: 8
  Total bibliography entries: 6
  Missing bibliography entries: 3
  Uncited references: 2

Status: INCONSISTENCIES FOUND
```

## Tips

1. **Make sure your bibliography section has a clear header** like "References", "Bibliography", or "Works Cited"

2. **Supported citation formats**:
   - APA: (Author, Year)
   - MLA: (Author Page)
   - IEEE/Numeric: [1]

3. **The tool will detect the citation style automatically** from your document

4. **For best results**, ensure your citations and bibliography entries follow standard formatting conventions

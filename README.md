# Citation Cross-Checker

A powerful tool that scans your manuscript drafts to ensure all in-text citations match your bibliography and vice versa, flagging any inconsistencies.

## Features

- **Multi-Format Support**: Handles APA, Harvard, Chicago, MLA, IEEE, and numeric citation styles
- **Bidirectional Checking**: Verifies citations have bibliography entries AND bibliography entries are cited
- **Detailed Reports**: Clear, color-coded output showing all inconsistencies
- **Year Mismatch Detection**: Identifies potential year mismatches (e.g., online-first vs. final publication)
- **Format Detection**: Automatically detects citation style from your document
- **Flexible Input**: Works with plain text, Markdown, LaTeX, and **Word (.docx)** files
- **Robust Parsing**: Correctly handles various bibliography formats including "LastName, FirstName" entries

## Installation

### From Source

```bash
pip install -e .
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

```bash
# Check a manuscript file (supports .txt, .md, .docx)
citation-checker check manuscript.txt

# Check a Word document
citation-checker check thesis.docx

# Specify custom bibliography section
citation-checker check manuscript.txt --bib-section "Works Cited"

# Export report to file
citation-checker check manuscript.txt --output report.txt

# Verbose mode
citation-checker check manuscript.txt --verbose
```

### Python API

```python
from citation_cross_checker import CitationChecker

# Initialize checker
checker = CitationChecker()

# Option 1: Check a file directly (supports .txt, .md, .docx)
result = checker.check_file('manuscript.txt')
# or
result = checker.check_file('thesis.docx')

# Option 2: Check text directly
with open('manuscript.txt', 'r') as f:
    text = f.read()
result = checker.check_document(text)

# Print report
print(result.generate_report())
```

## Supported Citation Formats

### APA Style
- In-text: `(Author, Year)`, `(Author et al., Year)`, `Author (Year)`
- Bibliography: `Author, A. (Year). Title...`

### Harvard Style
- In-text: `(Author Year)`, `(Author, Year)`, `Author (Year)`
- Bibliography: `Author, A. Year. Title...`

### Chicago Author-Date Style
- In-text: `(Author Year)`, `(Author, Year)`, `Author (Year)`
- Bibliography: `Author, First. Year. Title...`

### MLA Style
- In-text: `(Author Page)`, `(Author et al. Page)`
- Bibliography: `Author, First. "Title"...`

### IEEE/Numeric Style
- In-text: `[1]`, `[1-3]`, `[1,2,5]`
- Bibliography: `[1] Author, "Title"...`

## Examples

### Input Document

```text
Recent studies have shown significant results (Smith, 2020). Multiple
researchers agree (Johnson et al., 2021; Williams, 2019). However, some
findings remain controversial [3].

References:
Smith, J. (2020). A Study on Citations. Journal of Research, 15(2), 120-135.
Johnson, M., Lee, K., & Chen, R. (2021). Advanced Methods. Science Press.
Williams, A. (2019). Research Methodology. Academic Publishers.
Brown, T. (2018). Uncited Work. University Press.
```

### Output Report

```
Citation Cross-Checker Report
========================================

MISSING BIBLIOGRAPHY ENTRIES:
✗ Citation '[3]' found in text but missing from bibliography

UNCITED REFERENCES:
✗ 'Brown, T. (2018)' in bibliography but never cited in text

SUMMARY:
Total in-text citations: 4
Total bibliography entries: 4
Missing bibliography entries: 1
Uncited references: 1

Status: INCONSISTENCIES FOUND
```

## File Structure

```
citation-cross-checker/
├── src/
│   └── citation_cross_checker/
│       ├── __init__.py
│       ├── cli.py              # Command-line interface
│       ├── checker.py          # Main checking logic
│       ├── parsers.py          # Citation and bibliography parsers
│       ├── models.py           # Data models
│       └── formatters.py       # Output formatting
├── tests/
│   ├── test_checker.py
│   ├── test_parsers.py
│   └── fixtures/
│       └── sample_manuscripts.py
├── README.md
├── pyproject.toml
└── requirements.txt
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Running with Coverage

```bash
pytest --cov=citation_cross_checker --cov-report=html
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

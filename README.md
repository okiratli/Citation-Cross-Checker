# Citation Cross-Checker

A powerful tool that scans your manuscript drafts to ensure all in-text citations match your bibliography and vice versa, flagging any inconsistencies.

**Created by: Osman Sabri Kiratli**

## Features

- **🖥️ GUI Application**: Easy-to-use graphical interface for Windows (and cross-platform)
- **Multi-Format Support**: Handles APA, Harvard, Chicago, MLA, IEEE, and numeric citation styles
- **Bidirectional Checking**: Verifies citations have bibliography entries AND bibliography entries are cited
- **Detailed Reports**: Clear, color-coded output showing all inconsistencies
- **Year Mismatch Detection**: Identifies potential year mismatches (e.g., online-first vs. final publication)
- **Format Detection**: Automatically detects citation style from your document
- **Flexible Input**: Works with plain text, Markdown, LaTeX, and **Word (.docx)** files
- **Robust Parsing**: Correctly handles various bibliography formats including "LastName, FirstName" entries
- **Standalone .exe**: Can be packaged as a Windows executable (no Python required for end users)

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

### GUI Application (Recommended for Windows Users)

The easiest way to use Citation Cross-Checker is through the graphical interface:

#### Quick Start:
```bash
# After installation, simply run:
citation-checker-gui

# Or double-click (Windows):
launch_gui.bat
```

#### GUI Features:
- 📁 **Browse** to select your manuscript file (.txt, .md, .docx)
- ⚙️ **Configure** optional bibliography section name
- ▶️ **Click "Check Citations"** to run the analysis
- 📊 **View** color-coded results instantly
- 💾 **Save** report to a text file

#### Creating a Windows Executable:
See [BUILD_WINDOWS_EXE.md](BUILD_WINDOWS_EXE.md) for instructions to create a standalone `.exe` file that can be distributed to users without Python installed.

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
findings remain controversial [3]. Early work by Garcia (2022) established
the foundation.

References:
Smith, J. (2020). A Study on Citations. Journal of Research, 15(2), 120-135.
Johnson, M., Lee, K., & Chen, R. (2021). Advanced Methods. Science Press.
Williams, A. (2019). Research Methodology. Academic Publishers.
Brown, T. (2018). Uncited Work. University Press.
Garcia, P. (2023). Foundation Work. Research Quarterly, 12(1), 45-67.
```

### Output Report

```
Citation Cross-Checker Report
============================================================

MISSING BIBLIOGRAPHY ENTRIES:
✗ Citation '[3]' found in text but missing from bibliography

UNCITED REFERENCES:
✗ 'Brown, 2018' in bibliography but never cited in text

POTENTIAL YEAR MISMATCHES:
(Same authors cited and in bibliography, but with different years)
  ⚠  Citation: (Garcia, 2022) (year: 2022)
      Bibliography: Garcia, 2023 (year: 2023)

SUMMARY:
Total in-text citations: 5
Total bibliography entries: 5
Missing bibliography entries: 1
Uncited references: 1
Potential year mismatches: 1

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

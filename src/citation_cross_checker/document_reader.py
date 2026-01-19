"""Document reader utilities for various file formats."""

from pathlib import Path
from typing import Union


class DocumentReader:
    """Reads text from various document formats."""

    @staticmethod
    def read_file(file_path: Union[str, Path]) -> str:
        """
        Read text from a file.

        Supports:
        - Plain text files (.txt)
        - Markdown files (.md)
        - Word documents (.docx)

        Args:
            file_path: Path to the file

        Returns:
            Extracted text content

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is unsupported
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()

        if suffix in ['.txt', '.md', '.markdown', '.tex', '.latex']:
            return DocumentReader._read_text_file(file_path)
        elif suffix == '.docx':
            return DocumentReader._read_docx_file(file_path)
        else:
            # Try to read as text file anyway
            try:
                return DocumentReader._read_text_file(file_path)
            except Exception:
                raise ValueError(
                    f"Unsupported file format: {suffix}. "
                    f"Supported formats: .txt, .md, .docx"
                )

    @staticmethod
    def _read_text_file(file_path: Path) -> str:
        """Read a plain text file."""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()

    @staticmethod
    def _read_docx_file(file_path: Path) -> str:
        """Read a Word document (.docx) file."""
        try:
            from docx import Document
        except ImportError:
            raise ImportError(
                "python-docx is required to read .docx files. "
                "Install it with: pip install python-docx"
            )

        doc = Document(file_path)

        # Extract text from all paragraphs
        paragraphs = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                paragraphs.append(text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()
                    if text:
                        paragraphs.append(text)

        return '\n'.join(paragraphs)

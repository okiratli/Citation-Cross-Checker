"""Tests for document reader."""

import pytest
from pathlib import Path
from citation_cross_checker.document_reader import DocumentReader


class TestDocumentReader:
    """Test document reader functionality."""

    def test_read_text_file(self, tmp_path):
        """Test reading a plain text file."""
        # Create a temporary text file
        text_file = tmp_path / "test.txt"
        content = "This is a test document.\nWith multiple lines."
        text_file.write_text(content)

        result = DocumentReader.read_file(text_file)

        assert result == content

    def test_read_markdown_file(self, tmp_path):
        """Test reading a markdown file."""
        md_file = tmp_path / "test.md"
        content = "# Header\n\nSome content here."
        md_file.write_text(content)

        result = DocumentReader.read_file(md_file)

        assert result == content

    def test_file_not_found(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            DocumentReader.read_file("nonexistent_file.txt")

    def test_read_docx_file_import_error(self, tmp_path, monkeypatch):
        """Test that helpful error is raised when python-docx is not installed."""
        docx_file = tmp_path / "test.docx"
        docx_file.write_text("")  # Create empty file

        # Mock the import to fail
        import builtins
        real_import = builtins.__import__

        def mock_import(name, *args, **kwargs):
            if name == "docx":
                raise ImportError("No module named 'docx'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", mock_import)

        with pytest.raises(ImportError, match="python-docx is required"):
            DocumentReader.read_file(docx_file)

    def test_supported_extensions(self, tmp_path):
        """Test that various supported extensions work."""
        supported = [".txt", ".md", ".markdown"]

        for ext in supported:
            file_path = tmp_path / f"test{ext}"
            content = f"Content for {ext} file"
            file_path.write_text(content)

            result = DocumentReader.read_file(file_path)
            assert result == content

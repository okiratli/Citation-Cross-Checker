#!/usr/bin/env python3
"""
Diagnostic script to check endnote extraction from your Word document.

Usage:
    python diagnose_endnotes.py your_document.docx
"""

import sys
import logging
from pathlib import Path

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s: %(message)s'
)

def diagnose_document(docx_path):
    """Diagnose endnote extraction from a .docx file."""
    from src.citation_cross_checker.document_reader import DocumentReader
    from src.citation_cross_checker.parsers import CitationParser

    print("=" * 80)
    print(f"ENDNOTE DIAGNOSTIC REPORT: {docx_path}")
    print("=" * 80)

    docx_path = Path(docx_path)

    if not docx_path.exists():
        print(f"✗ ERROR: File not found: {docx_path}")
        return False

    if not docx_path.suffix.lower() == '.docx':
        print(f"✗ ERROR: Not a .docx file: {docx_path}")
        print(f"  File extension: {docx_path.suffix}")
        return False

    print(f"✓ File found: {docx_path}")
    print(f"  Size: {docx_path.stat().st_size:,} bytes")
    print()

    # Step 1: Check if endnotes.xml exists in the .docx
    print("STEP 1: Checking for endnotes.xml in .docx archive")
    print("-" * 80)

    import zipfile
    try:
        with zipfile.ZipFile(docx_path, 'r') as docx_zip:
            files = docx_zip.namelist()
            print(f"Found {len(files)} files in .docx archive")

            has_endnotes = 'word/endnotes.xml' in files
            has_footnotes = 'word/footnotes.xml' in files

            if has_endnotes:
                print("✓ word/endnotes.xml EXISTS")

                # Show a preview of the endnotes XML
                endnotes_xml = docx_zip.read('word/endnotes.xml')
                print(f"  Size: {len(endnotes_xml):,} bytes")
                print(f"  Preview (first 500 chars):")
                print("  " + "-" * 76)
                print("  " + endnotes_xml[:500].decode('utf-8', errors='replace'))
                print("  " + "-" * 76)
            else:
                print("✗ word/endnotes.xml NOT FOUND")
                print("  This document may not have endnotes, or they may be stored differently")

            if has_footnotes:
                print("✓ word/footnotes.xml EXISTS")
            else:
                print("  word/footnotes.xml not found")

    except zipfile.BadZipFile:
        print("✗ ERROR: File is not a valid .docx (ZIP archive)")
        return False
    except Exception as e:
        print(f"✗ ERROR reading .docx structure: {e}")
        return False

    print()

    # Step 2: Try to extract endnotes
    print("STEP 2: Attempting to extract endnotes")
    print("-" * 80)

    try:
        endnotes_text = DocumentReader._extract_docx_notes(docx_path, 'endnotes')

        if endnotes_text:
            lines = endnotes_text.split('\n')
            print(f"✓ Successfully extracted {len(lines)} endnotes")
            print(f"\nExtracted endnotes:")
            print("=" * 80)
            print(endnotes_text)
            print("=" * 80)
        else:
            print("✗ No endnotes extracted (empty result)")
            print("  Possible reasons:")
            print("  - Document has no endnotes")
            print("  - Endnotes file exists but contains no content")
            print("  - XML structure is different than expected")

    except Exception as e:
        print(f"✗ ERROR extracting endnotes: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Step 3: Extract full document text
    print("STEP 3: Extracting full document text (including endnotes)")
    print("-" * 80)

    try:
        full_text = DocumentReader.read_file(docx_path)
        print(f"✓ Extracted {len(full_text)} characters total")

        if "Endnotes:" in full_text:
            print("✓ 'Endnotes:' section found in extracted text")

            # Show the endnotes section
            endnotes_start = full_text.find("Endnotes:")
            endnotes_section = full_text[endnotes_start:endnotes_start + 2000]
            print(f"\nEndnotes section preview:")
            print("=" * 80)
            print(endnotes_section)
            print("=" * 80)
        else:
            print("✗ 'Endnotes:' section NOT found in extracted text")
            print(f"\nFull extracted text preview (last 1000 chars):")
            print("=" * 80)
            print(full_text[-1000:])
            print("=" * 80)

    except Exception as e:
        print(f"✗ ERROR reading document: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Step 4: Parse citations
    print("STEP 4: Parsing citations from extracted text")
    print("-" * 80)

    try:
        parser = CitationParser()
        citations = parser.parse(full_text)

        print(f"✓ Found {len(citations)} citations total")

        if citations:
            print(f"\nAll citations found:")
            for i, cite in enumerate(citations, 1):
                print(f"  {i}. {cite.raw_text}")
                print(f"     Authors: {cite.authors}, Year: {cite.year}")
                print(f"     Position in text: {cite.position}")
        else:
            print("✗ No citations found")

    except Exception as e:
        print(f"✗ ERROR parsing citations: {e}")
        import traceback
        traceback.print_exc()
        return False

    print()

    # Step 5: Search for specific citations from the screenshot
    print("STEP 5: Searching for specific citations from your endnotes")
    print("-" * 80)

    test_citations = [
        ("Aytaç", "2018"),
        ("Elçi", "2018"),
        ("Suuronen", "2025"),
        ("Levitsky", "2025"),
        ("Ziblatt", "2025"),
        ("Almond", "1963"),
        ("Verba", "1963"),
        ("Dalton", "2007"),
    ]

    for author, year in test_citations:
        # Check if in raw text
        in_text = author in full_text

        # Check if parsed as citation
        found_citation = any(
            author in cite.authors and cite.year == year
            for cite in citations
        )

        status = "✓" if found_citation else "✗"
        print(f"{status} {author} ({year})")
        print(f"   In extracted text: {in_text}")
        print(f"   Parsed as citation: {found_citation}")

    print()
    print("=" * 80)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 80)

    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python diagnose_endnotes.py your_document.docx")
        sys.exit(1)

    docx_path = sys.argv[1]
    success = diagnose_document(docx_path)
    sys.exit(0 if success else 1)

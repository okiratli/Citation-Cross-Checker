#!/usr/bin/env python3
"""Diagnostic script to debug the Moral & Best citation issue.

Run this with your actual manuscript file to see what's happening.
"""

import sys
sys.path.insert(0, 'src')

from citation_cross_checker.checker import CitationChecker
from citation_cross_checker.parsers import CitationParser, BibliographyParser

# You can either:
# 1. Pass your file path as argument: python diagnose.py yourfile.docx
# 2. Or paste a sample of your text below

if len(sys.argv) > 1:
    # Read from file
    from citation_cross_checker.document_reader import DocumentReader
    file_path = sys.argv[1]
    print(f"Reading file: {file_path}")
    text = DocumentReader.read_file(file_path)
else:
    # Use sample text - REPLACE THIS with your actual text
    text = """
PASTE YOUR DOCUMENT TEXT HERE INCLUDING:
- The paragraph with the footnote marker
- The Notes section with "3 Moral & Best (2023) present ..."
- The References section with the Moral & Best entry
"""

print("="*70)
print("DIAGNOSTIC ANALYSIS")
print("="*70)

# Step 1: Show what the bibliography extractor finds
print("\n1. BIBLIOGRAPHY EXTRACTION")
print("-"*70)
bib_parser = BibliographyParser()
bib_entries, bib_text = bib_parser.parse(text)

print(f"Bibliography text (first 500 chars):")
print(repr(bib_text[:500]))
print(f"\nBibliography entries found: {len(bib_entries)}")
for entry in bib_entries:
    print(f"  - Key: {entry.get_key()}")
    print(f"    Authors: {entry.authors}")
    print(f"    Year: {entry.year}")
    print(f"    Raw (first 100 chars): {entry.raw_text[:100]}")
    print()

# Step 2: Show what citations are found
print("\n2. CITATION PARSING")
print("-"*70)
cite_parser = CitationParser()
citations = cite_parser.parse(text)

print(f"Citations found: {len(citations)}")
for i, cit in enumerate(citations, 1):
    print(f"  {i}. '{cit.raw_text}'")
    print(f"     Authors: {cit.authors}")
    print(f"     Year: {cit.year}")
    print(f"     Type: {cit.citation_type}")
    print(f"     Position in document: {cit.position}")
    # Show context around the citation
    start = max(0, cit.position - 30)
    end = min(len(text), cit.position + len(cit.raw_text) + 30)
    context = text[start:end]
    print(f"     Context: ...{repr(context)}...")
    print()

# Step 3: Check which citations match which bibliography entries
print("\n3. CITATION-BIBLIOGRAPHY MATCHING")
print("-"*70)
for cit in citations:
    print(f"\nCitation: {cit.raw_text}")
    print(f"  Authors: {cit.authors}, Year: {cit.year}")
    matched = False
    for bib in bib_entries:
        if cit.matches_bib(bib):
            print(f"  ✓ MATCHES: {bib.get_key()}")
            matched = True
            break
    if not matched:
        print(f"  ✗ NO MATCH FOUND")

# Step 4: Run full checker
print("\n4. FULL CHECKER RESULTS")
print("-"*70)
checker = CitationChecker()
result = checker.check_document(text)

if result.missing_bib_entries:
    print(f"\n❌ Missing bibliography entries ({len(result.missing_bib_entries)}):")
    for missing in result.missing_bib_entries:
        print(f"  ✗ {missing.raw_text}")
        print(f"    Authors: {missing.authors}, Year: {missing.year}")

if result.uncited_references:
    print(f"\n❌ Uncited references ({len(result.uncited_references)}):")
    for uncited in result.uncited_references:
        print(f"  ✗ {uncited.get_key()}")
        print(f"    Authors: {uncited.authors}, Year: {uncited.year}")
        print(f"    Raw: {uncited.raw_text[:100]}")

if result.year_mismatches:
    print(f"\n⚠ Year mismatches ({len(result.year_mismatches)}):")
    for mm in result.year_mismatches:
        print(f"  {mm}")

if not result.has_issues():
    print("\n✅ NO ISSUES FOUND")

# Step 5: Search for "Moral" in the document
print("\n5. SEARCHING FOR 'Moral' IN DOCUMENT")
print("-"*70)
import re
moral_matches = list(re.finditer(r'Moral[^a-z].*?(?:\n|$)', text, re.IGNORECASE))
print(f"Found {len(moral_matches)} occurrences of 'Moral':")
for i, match in enumerate(moral_matches[:10], 1):  # Show first 10
    print(f"  {i}. Position {match.start()}: {repr(match.group(0)[:80])}")

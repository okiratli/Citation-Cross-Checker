# Citation Cross-Checker - GUI User Guide

Welcome to the Citation Cross-Checker! This guide will help you use the graphical interface to check your manuscript citations.

## Starting the Application

### If you have Python installed:
1. Double-click `launch_gui.bat` (Windows)
2. Or run: `python launch_gui.py`

### If you have the .exe file:
1. Double-click `Citation-Cross-Checker.exe`
2. No Python installation required!

## How to Use

### Step 1: Select Your Manuscript File

1. Click the **"Browse..."** button
2. Navigate to your manuscript file
3. Select a file (supports .txt, .md, .docx)
4. Click "Open"

The selected file name will appear in the window.

### Step 2: (Optional) Specify Bibliography Section

If your bibliography section has a custom name (like "Works Cited" instead of "References"), enter it in the **"Bibliography Section Name"** field.

**Common names:**
- References (default)
- Bibliography
- Works Cited
- Literature Cited

Leave this blank if your section is called "References".

### Step 3: Check Citations

Click the **"Check Citations"** button.

The tool will analyze your manuscript and display results in the main window.

### Step 4: Review Results

The results are color-coded for easy reading:

🔴 **Red (Missing Bibliography Entries)**
- Citations found in your text that don't have matching bibliography entries
- **Action needed:** Add these references to your bibliography

🟠 **Orange/Yellow (Uncited References)**
- Bibliography entries that are never cited in your text
- **Action needed:** Either cite these in your text or remove from bibliography

🔵 **Blue (Year Mismatches)**
- Same author cited with different years in text vs. bibliography
- **Common cause:** Online-first publication changed year when officially published
- **Action needed:** Update the year in your citation or bibliography to match

🟢 **Green (Success)**
- Indicates checks that passed
- All citations match, all references are cited

### Step 5: Save Report (Optional)

1. Click **"Save Report"** button
2. Choose where to save the file
3. Enter a filename (e.g., "citation_report.txt")
4. Click "Save"

You can share this report with colleagues or keep it for your records.

## Understanding the Results

### Example Output:

```
Citation Cross-Checker Report
============================================================

MISSING BIBLIOGRAPHY ENTRIES:
  ✗ Citation '(Smith, 2023)' found in text but missing from bibliography

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

### What This Means:

1. **Missing Entry:** You cited Smith (2023) in your text, but there's no Smith 2023 in your bibliography
2. **Uncited Reference:** You have Brown 2018 in your bibliography, but never cited it in the text
3. **Year Mismatch:** You cited Garcia (2022) in your text, but your bibliography shows Garcia 2023

### How to Fix:

1. **For missing entries:** Add the reference to your bibliography
2. **For uncited references:** Either cite it in your text or remove from bibliography
3. **For year mismatches:** Make the years consistent (usually update to the final publication year)

## Tips for Best Results

### ✅ DO:
- Save your manuscript in a supported format (.txt, .md, .docx)
- Use standard citation formats (APA, Harvard, Chicago, MLA, IEEE)
- Label your bibliography section clearly ("References", "Bibliography", etc.)
- Run the checker before submitting your manuscript

### ❌ DON'T:
- Use image-based PDFs (convert to text first)
- Mix citation styles inconsistently
- Forget to save your corrected manuscript!

## Supported Citation Styles

### Author-Year Styles:
- **APA:** (Smith, 2020)
- **Harvard:** (Smith 2020) or (Smith, 2020)
- **Chicago:** (Brown 2019)

### Other Styles:
- **MLA:** (Smith 45-67)
- **IEEE/Numeric:** [1], [2-5]

All styles can be mixed in the same document!

## Troubleshooting

### "No bibliography entries found"
- Check that your bibliography section has a clear header
- Try entering the exact section name in "Bibliography Section Name"
- Make sure references are formatted consistently

### "No citations found"
- Check that your citations follow standard formats
- Make sure citations are properly formatted with parentheses or brackets

### "Some citations not detected"
- Check citation format matches supported styles
- Ensure proper use of commas and spaces
- For unusual formats, citations may not be detected

## Getting Help

If you encounter issues:
1. Check this guide
2. Review the example files in the `examples/` folder
3. Consult the full README.md for technical details
4. Report issues on GitHub

## Example Workflow

Here's a typical workflow:

1. **Write your manuscript** with citations
2. **Add bibliography** at the end
3. **Run Citation Checker** using this GUI
4. **Review results** - note any issues
5. **Fix issues** in your manuscript
   - Add missing bibliography entries
   - Cite or remove uncited references
   - Correct year mismatches
6. **Run checker again** to verify fixes
7. **Save final report** for your records
8. **Submit clean manuscript!** ✅

## Keyboard Shortcuts

- **Alt+B:** Browse for file (when button is focused)
- **Alt+C:** Check citations (when file is selected)
- **Alt+S:** Save report (when results are available)

## Privacy & Security

- All processing is done **locally on your computer**
- No data is sent to external servers
- Your manuscripts remain private
- No internet connection required

Enjoy using Citation Cross-Checker!

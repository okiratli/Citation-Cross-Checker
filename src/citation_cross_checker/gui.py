"""GUI application for Citation Cross-Checker."""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import sys

from .checker import CitationChecker


class CitationCheckerGUI:
    """GUI application for Citation Cross-Checker."""

    def __init__(self, root):
        self.root = root
        self.root.title("Citation Cross-Checker")
        self.root.geometry("900x700")

        # Initialize checker
        self.checker = CitationChecker()
        self.current_file = None

        # Configure style
        self.setup_styles()

        # Create GUI elements
        self.create_widgets()

    def setup_styles(self):
        """Setup ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')

    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="View README", command=self.show_readme)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self.show_about)

    def show_readme(self):
        """Show README content in a new window."""
        readme_window = tk.Toplevel(self.root)
        readme_window.title("README - Citation Cross-Checker")
        readme_window.geometry("800x600")

        # Create scrolled text widget
        text_widget = scrolledtext.ScrolledText(
            readme_window,
            wrap=tk.WORD,
            width=80,
            height=30,
            font=('Courier', 10)
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Try to load README.md from package directory
        readme_content = self.get_readme_content()
        text_widget.insert(tk.END, readme_content)
        text_widget.config(state='disabled')  # Make read-only

    def get_readme_content(self):
        """Get README content from file or return default text."""
        try:
            # Try to find README.md in various locations
            possible_paths = [
                Path(__file__).parent.parent.parent.parent / "README.md",
                Path.cwd() / "README.md",
            ]

            for path in possible_paths:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        return f.read()

            # If README not found, return embedded content
            return self.get_embedded_readme()

        except Exception as e:
            return f"Error loading README: {str(e)}\n\nPlease visit the GitHub repository for documentation."

    def get_embedded_readme(self):
        """Return embedded README content."""
        return """# Citation Cross-Checker

A powerful tool that scans your manuscript drafts to ensure all in-text citations
match your bibliography and vice versa, flagging any inconsistencies.

Created by: Osman Sabri Kiratli

## Features

- Multi-Format Support: APA, Harvard, Chicago, MLA, IEEE, and numeric citations
- Bidirectional Checking: Verifies citations have bibliography entries AND vice versa
- Year Mismatch Detection: Identifies potential year mismatches (online-first publications)
- Document Support: Works with .txt, .md, .docx, and .pdf files
- GUI Application: Easy-to-use graphical interface

## Supported Citation Formats

### APA Style
- In-text: (Author, Year), (Author et al., Year), Author (Year)
- Bibliography: Author, A. (Year). Title...

### Harvard Style
- In-text: (Author Year), Author (Year)
- Bibliography: Author, A. Year. Title...

### Chicago Style
- In-text: (Author Year), Author (Year)
- Bibliography: Author, First. Year. Title...

### MLA Style
- In-text: (Author Page)
- Bibliography: Author, First. "Title"...

### IEEE/Numeric
- In-text: [1], [1-3], [1,2,5]
- Bibliography: [1] Author, "Title"...

## How to Use

1. Click "Browse..." to select your manuscript file
2. (Optional) Enter bibliography section name if different from "References"
3. Click "Check Citations" to run the analysis
4. Review color-coded results:
   - RED: Missing bibliography entries
   - YELLOW: Uncited references
   - BLUE: Potential year mismatches
   - GREEN: Success messages
5. Click "Save Report" to export results (optional)

## Understanding Results

### Missing Bibliography Entries
Citations found in your text that don't have matching bibliography entries.
Action: Add these references to your bibliography.

### Uncited References
Bibliography entries that are never cited in your text.
Action: Either cite them or remove from bibliography.

### Potential Year Mismatches
Same authors cited with different years (common with online-first publications).
Action: Update the year to match final publication.

## Tips

- Use standard citation formats for best results
- Label your bibliography section clearly
- Run the checker before submitting manuscripts
- All processing is done locally - your documents remain private

## License

MIT License

Created by: Osman Sabri Kiratli
GitHub: https://github.com/okiratli/abc

For more information, visit the GitHub repository.
"""

    def show_about(self):
        """Show about dialog."""
        about_text = """Citation Cross-Checker
Version 1.0.0

A powerful tool for checking citation consistency in academic manuscripts.

Created by: Osman Sabri Kiratli

Supports:
• APA, Harvard, Chicago, MLA, IEEE citation styles
• Word documents (.docx), text files (.txt, .md), PDF files (.pdf)
• Bidirectional citation checking
• Year mismatch detection

© 2026 Osman Sabri Kiratli
Licensed under MIT License

GitHub: https://github.com/okiratli/abc
"""
        messagebox.showinfo("About Citation Cross-Checker", about_text)

    def create_widgets(self):
        """Create all GUI widgets."""
        # Create menu bar
        self.create_menu()

        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Citation Cross-Checker",
            font=('Arial', 16, 'bold')
        )
        title_label.grid(row=0, column=0, pady=(0, 10), sticky=tk.W)

        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="Select Manuscript File", padding="10")
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        self.file_label = ttk.Label(file_frame, text="No file selected")
        self.file_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Button(
            file_frame,
            text="Browse...",
            command=self.browse_file
        ).grid(row=1, column=0, sticky=tk.W)

        ttk.Label(
            file_frame,
            text="Supported: .txt, .md, .docx, .pdf",
            font=('Arial', 9, 'italic')
        ).grid(row=1, column=1, sticky=tk.W, padx=(10, 0))

        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(1, weight=1)

        ttk.Label(options_frame, text="Bibliography Section Name:").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )

        self.bib_section_var = tk.StringVar()
        bib_section_entry = ttk.Entry(
            options_frame,
            textvariable=self.bib_section_var,
            width=30
        )
        bib_section_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(
            options_frame,
            text='(Optional, e.g., "Works Cited")',
            font=('Arial', 9, 'italic')
        ).grid(row=0, column=2, sticky=tk.W, padx=(10, 0))

        # Action buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, pady=(0, 10))

        self.check_button = ttk.Button(
            button_frame,
            text="Check Citations",
            command=self.check_citations,
            state='disabled'
        )
        self.check_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(
            button_frame,
            text="Save Report",
            command=self.save_report,
            state='disabled'
        )
        self.save_button.grid(row=0, column=1, padx=5)

        ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_results
        ).grid(row=0, column=2, padx=5)

        # Results frame
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
        results_frame.grid(row=4, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)

        # Results text area with scrollbar
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=('Courier', 10)
        )
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure text tags for colors
        self.results_text.tag_configure('error', foreground='red')
        self.results_text.tag_configure('warning', foreground='orange')
        self.results_text.tag_configure('info', foreground='blue')
        self.results_text.tag_configure('success', foreground='green')
        self.results_text.tag_configure('bold', font=('Courier', 10, 'bold'))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=5, column=0, sticky=(tk.W, tk.E))

    def browse_file(self):
        """Open file dialog to select manuscript file."""
        filename = filedialog.askopenfilename(
            title="Select Manuscript File",
            filetypes=[
                ("All Supported", "*.txt *.md *.docx *.pdf"),
                ("Text Files", "*.txt"),
                ("Markdown Files", "*.md"),
                ("Word Documents", "*.docx"),
                ("PDF Documents", "*.pdf"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            self.current_file = filename
            self.file_label.config(text=Path(filename).name)
            self.check_button.config(state='normal')
            self.status_var.set(f"File loaded: {Path(filename).name}")

    def check_citations(self):
        """Run citation check on selected file."""
        if not self.current_file:
            messagebox.showwarning("No File", "Please select a manuscript file first.")
            return

        try:
            self.status_var.set("Checking citations...")
            self.root.update_idletasks()

            # Get optional bibliography section name
            bib_section = self.bib_section_var.get().strip() or None

            # Run check
            result = self.checker.check_file(self.current_file, bib_section)

            # Display results
            self.display_results(result)

            # Update status
            if result.has_issues():
                self.status_var.set("Check complete - Issues found")
            else:
                self.status_var.set("Check complete - All checks passed!")

            # Enable save button
            self.save_button.config(state='normal')

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred:\n\n{str(e)}")
            self.status_var.set("Error occurred")

    def display_results(self, result):
        """Display check results in the text area."""
        self.results_text.delete(1.0, tk.END)

        # Header
        self.insert_bold("Citation Cross-Checker Report\n")
        self.results_text.insert(tk.END, "=" * 70 + "\n\n")

        # Missing bibliography entries
        if result.missing_bib_entries:
            self.insert_bold("MISSING BIBLIOGRAPHY ENTRIES:\n", 'error')
            for citation in result.missing_bib_entries:
                self.results_text.insert(
                    tk.END,
                    f"  ✗ Citation '{citation.raw_text}' found in text but missing from bibliography\n",
                    'error'
                )
            self.results_text.insert(tk.END, "\n")
        else:
            self.results_text.insert(
                tk.END,
                "✓ All citations have bibliography entries\n\n",
                'success'
            )

        # Uncited references
        if result.uncited_references:
            self.insert_bold("UNCITED REFERENCES:\n", 'warning')
            for bib_entry in result.uncited_references:
                key = bib_entry.get_key()
                self.results_text.insert(
                    tk.END,
                    f"  ✗ '{key}' in bibliography but never cited in text\n",
                    'warning'
                )
            self.results_text.insert(tk.END, "\n")
        else:
            self.results_text.insert(
                tk.END,
                "✓ All bibliography entries are cited\n\n",
                'success'
            )

        # Year mismatches
        if result.year_mismatches:
            self.insert_bold("POTENTIAL YEAR MISMATCHES:\n", 'info')
            self.results_text.insert(
                tk.END,
                "(Same authors cited and in bibliography, but with different years)\n",
                'info'
            )
            for mismatch in result.year_mismatches:
                citation_year = mismatch.citation.year
                bib_year = mismatch.bib_entry.year
                bib_key = mismatch.bib_entry.get_key()
                self.results_text.insert(
                    tk.END,
                    f"  ⚠  Citation: {mismatch.citation.raw_text} (year: {citation_year})\n",
                    'info'
                )
                self.results_text.insert(
                    tk.END,
                    f"      Bibliography: {bib_key} (year: {bib_year})\n",
                    'info'
                )
            self.results_text.insert(tk.END, "\n")

        # Summary
        self.insert_bold("SUMMARY:\n")
        self.results_text.insert(tk.END, f"  Total in-text citations: {len(result.citations)}\n")
        self.results_text.insert(tk.END, f"  Total bibliography entries: {len(result.bib_entries)}\n")
        self.results_text.insert(tk.END, f"  Missing bibliography entries: {len(result.missing_bib_entries)}\n")
        self.results_text.insert(tk.END, f"  Uncited references: {len(result.uncited_references)}\n")
        self.results_text.insert(tk.END, f"  Potential year mismatches: {len(result.year_mismatches)}\n\n")

        # Status
        self.insert_bold("Status: ")
        if result.has_issues():
            self.results_text.insert(tk.END, "INCONSISTENCIES FOUND\n", 'error')
        else:
            self.results_text.insert(tk.END, "ALL CHECKS PASSED\n", 'success')

    def insert_bold(self, text, tag=None):
        """Insert bold text with optional additional tag."""
        if tag:
            self.results_text.insert(tk.END, text, ('bold', tag))
        else:
            self.results_text.insert(tk.END, text, 'bold')

    def save_report(self):
        """Save the report to a file."""
        if not self.results_text.get(1.0, tk.END).strip():
            messagebox.showwarning("No Report", "No report to save.")
            return

        filename = filedialog.asksaveasfilename(
            title="Save Report",
            defaultextension=".txt",
            filetypes=[
                ("Text Files", "*.txt"),
                ("All Files", "*.*")
            ]
        )

        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.results_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"Report saved to:\n{filename}")
                self.status_var.set(f"Report saved to {Path(filename).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report:\n\n{str(e)}")

    def clear_results(self):
        """Clear the results text area."""
        self.results_text.delete(1.0, tk.END)
        self.save_button.config(state='disabled')
        self.status_var.set("Results cleared")


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = CitationCheckerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()

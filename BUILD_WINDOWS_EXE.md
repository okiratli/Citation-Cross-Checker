# Building a Windows Executable (.exe)

This guide explains how to create a standalone Windows executable for the Citation Cross-Checker GUI application.

## Prerequisites

1. **Python 3.8 or higher** installed on Windows
2. **All dependencies** installed

## Method 1: Quick Launch (No Building Required)

### Option A: Using the Batch File
1. Double-click `launch_gui.bat`
2. The GUI will open automatically

### Option B: Using Python Directly
```cmd
python launch_gui.py
```

## Method 2: Create Standalone .exe with PyInstaller

### Step 1: Install PyInstaller

```cmd
pip install pyinstaller
```

### Step 2: Create the Executable

Navigate to the project directory and run:

```cmd
pyinstaller --name="Citation-Cross-Checker" ^
            --windowed ^
            --onefile ^
            --add-data "src/citation_cross_checker;citation_cross_checker" ^
            --icon=NONE ^
            launch_gui.py
```

**Explanation of flags:**
- `--name`: Name of the executable
- `--windowed`: Hide console window (GUI mode)
- `--onefile`: Bundle everything into a single .exe file
- `--add-data`: Include the source code
- `launch_gui.py`: The entry point script

### Step 3: Find Your Executable

After building, your executable will be in:
```
dist/Citation-Cross-Checker.exe
```

You can distribute this single .exe file to anyone with Windows!

### Step 4: (Optional) Create an Installer

For a more professional distribution, you can create an installer:

1. **Using Inno Setup (Free):**
   - Download from: https://jrsoftware.org/isinfo.php
   - Create a simple installer script

2. **Using NSIS (Free):**
   - Download from: https://nsis.sourceforge.io/

## Method 3: Using Auto-py-to-exe (GUI for PyInstaller)

For a visual interface:

### Step 1: Install auto-py-to-exe

```cmd
pip install auto-py-to-exe
```

### Step 2: Launch the GUI

```cmd
auto-py-to-exe
```

### Step 3: Configure Settings

1. **Script Location**: Select `launch_gui.py`
2. **Onefile**: Select "One File"
3. **Console Window**: Select "Window Based" (hide console)
4. **Additional Files**: Add `src/citation_cross_checker` folder
5. Click "Convert .py to .exe"

## Troubleshooting

### Issue: "Module not found" error

**Solution**: Make sure all dependencies are installed:
```cmd
pip install -r requirements.txt
```

### Issue: Antivirus blocks the .exe

**Solution**: This is common with PyInstaller executables. You may need to:
1. Add an exception in your antivirus
2. Sign the executable with a code signing certificate (for distribution)

### Issue: .exe is very large

**Solution**: This is normal. The .exe includes Python and all libraries.
- Typical size: 15-25 MB
- This is acceptable for standalone distribution

## Distribution

Once you have `Citation-Cross-Checker.exe`:

1. **Share the single .exe file** - Recipients can run it without Python installed
2. **Create a ZIP file** with:
   - `Citation-Cross-Checker.exe`
   - `README.md`
   - Example files (optional)

3. **Upload to GitHub Releases** for easy distribution

## Advanced: Creating an Icon

To add a custom icon:

1. Create or download a `.ico` file
2. Replace `--icon=NONE` with `--icon=path/to/your/icon.ico`

## Running the Development Version

If you want to run the GUI without building:

```cmd
# Install in development mode
pip install -e .

# Run the GUI
citation-checker-gui
```

Or simply:
```cmd
python launch_gui.py
```

## System Requirements for End Users

**When using the .exe:**
- Windows 7 or higher
- No Python installation required
- No additional dependencies required
- ~100 MB RAM

**When using Python scripts:**
- Windows 7 or higher
- Python 3.8 or higher
- Dependencies from requirements.txt

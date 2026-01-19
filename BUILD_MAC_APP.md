# Building Citation Cross-Checker for macOS

This guide will help you create a standalone macOS application (.app bundle) that Mac users can run without installing Python.

## Prerequisites

- macOS computer (required for building Mac apps)
- Python 3.8 or higher installed
- The Citation Cross-Checker source code

## Method 1: Using PyInstaller (Recommended)

PyInstaller can create a standalone .app bundle for macOS.

### Step 1: Install PyInstaller

```bash
pip install pyinstaller
```

### Step 2: Create the .app Bundle

From the project root directory, run:

```bash
pyinstaller --name="Citation-Cross-Checker" \
    --windowed \
    --onefile \
    --icon=icon.icns \
    --add-data "README.md:." \
    src/citation_cross_checker/gui.py
```

**Command explanation:**
- `--name="Citation-Cross-Checker"`: Sets the application name
- `--windowed`: Creates a GUI app (no terminal window)
- `--onefile`: Bundles everything into a single executable
- `--icon=icon.icns`: Sets the app icon (optional, see below)
- `--add-data "README.md:."`: Includes README in the bundle

### Step 3: Find Your App

After building, the application will be located at:
```
dist/Citation-Cross-Checker.app
```

You can now:
- Double-click to run it
- Move it to your Applications folder
- Distribute it to other Mac users

## Method 2: Using py2app (Mac-Native Alternative)

py2app is specifically designed for macOS and creates more Mac-native apps.

### Step 1: Install py2app

```bash
pip install py2app
```

### Step 2: Create setup.py

Create a file called `setup_mac.py` in your project root:

```python
from setuptools import setup

APP = ['src/citation_cross_checker/gui.py']
DATA_FILES = [('', ['README.md'])]
OPTIONS = {
    'argv_emulation': True,
    'packages': ['tkinter', 'citation_cross_checker'],
    'iconfile': 'icon.icns',  # Optional
    'plist': {
        'CFBundleName': 'Citation Cross-Checker',
        'CFBundleDisplayName': 'Citation Cross-Checker',
        'CFBundleGetInfoString': "Check citation consistency",
        'CFBundleIdentifier': "com.osmankiratli.citationchecker",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': 'Copyright © 2024 Osman Sabri Kiratli. All rights reserved.'
    }
}

setup(
    name='Citation Cross-Checker',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
```

### Step 3: Build the App

```bash
python setup_mac.py py2app
```

The app will be created in `dist/Citation Cross-Checker.app`

## Creating an App Icon (Optional)

To create a proper macOS icon (.icns file):

### Option A: Using Online Converter
1. Create a 1024x1024 PNG image of your icon
2. Use an online converter like [cloudconvert.com](https://cloudconvert.com/png-to-icns)
3. Save as `icon.icns` in your project root

### Option B: Using iconutil (Mac Only)
1. Create a folder structure with different icon sizes
2. Run: `iconutil -c icns icon.iconset`

For now, you can skip the icon and the app will use the default Python icon.

## Distributing Your Mac App

### Option 1: Simple Distribution (For Personal Use)
- Compress the .app bundle: Right-click → Compress "Citation-Cross-Checker.app"
- Share the .zip file
- **Note:** Users may see "unidentified developer" warning (see Gatekeeper below)

### Option 2: DMG Installer (Professional)

Create a disk image (.dmg) for easier distribution:

```bash
# Install create-dmg
brew install create-dmg

# Create DMG
create-dmg \
  --volname "Citation Cross-Checker" \
  --window-pos 200 120 \
  --window-size 600 400 \
  --icon-size 100 \
  --icon "Citation-Cross-Checker.app" 175 120 \
  --hide-extension "Citation-Cross-Checker.app" \
  --app-drop-link 425 120 \
  "Citation-Cross-Checker-Installer.dmg" \
  "dist/"
```

Users can then:
1. Open the .dmg file
2. Drag the app to their Applications folder
3. Eject the disk image

## Handling macOS Gatekeeper

When distributing to other users, they may see a warning: "Citation-Cross-Checker.app cannot be opened because it is from an unidentified developer."

### For Users to Bypass (Without Code Signing):
1. **Right-click** (or Control-click) the app → **Open**
2. Click **Open** in the dialog
3. The app will now run (and won't ask again)

**Alternative:**
- Go to System Preferences → Security & Privacy
- Click "Open Anyway" next to the blocked app message

### For Developers: Code Signing (Advanced)

To remove warnings entirely, you need:
1. An Apple Developer account ($99/year)
2. A Developer ID certificate
3. Code sign the app:

```bash
codesign --deep --force --sign "Developer ID Application: Your Name" \
  dist/Citation-Cross-Checker.app
```

4. Notarize with Apple:

```bash
xcrun notarytool submit Citation-Cross-Checker.zip \
  --apple-id "your@email.com" \
  --team-id "TEAMID" \
  --password "app-specific-password"
```

## Universal Binary (Intel + Apple Silicon)

To create an app that works on both Intel and Apple Silicon Macs:

```bash
pyinstaller --name="Citation-Cross-Checker" \
    --windowed \
    --onefile \
    --target-arch universal2 \
    src/citation_cross_checker/gui.py
```

**Note:** This requires running on macOS 11+ and may increase app size.

## Testing Your App

Before distributing:

1. **Test on your Mac:**
   - Double-click the .app bundle
   - Test all features (Browse, Check, Save Report)
   - Check the Help menu

2. **Test on another Mac (if possible):**
   - Copy to a different Mac
   - Test the Gatekeeper bypass process
   - Verify all features work

3. **Test with different file types:**
   - .txt files
   - .docx files
   - .md files

## Troubleshooting

### "Command not found: pyinstaller"
```bash
pip install --upgrade pyinstaller
# or
pip3 install --upgrade pyinstaller
```

### "No module named 'python-docx'"
Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### App crashes on startup
Run from terminal to see errors:
```bash
./dist/Citation-Cross-Checker.app/Contents/MacOS/Citation-Cross-Checker
```

### Large app size
The app may be 50-100MB because it includes the entire Python interpreter. This is normal.

### "Operation not permitted" when building
Make sure your terminal has Full Disk Access:
- System Preferences → Security & Privacy → Privacy → Full Disk Access
- Add Terminal or your IDE

## Quick Reference

**Build with PyInstaller (simple):**
```bash
pyinstaller --name="Citation-Cross-Checker" --windowed --onefile src/citation_cross_checker/gui.py
```

**Build with py2app:**
```bash
python setup_mac.py py2app
```

**Result location:**
```
dist/Citation-Cross-Checker.app
```

**Distribute:**
- Compress and share the .zip
- Or create a DMG installer
- Users: Right-click → Open to bypass Gatekeeper

## Additional Resources

- [PyInstaller Documentation](https://pyinstaller.org/en/stable/)
- [py2app Documentation](https://py2app.readthedocs.io/)
- [Apple Code Signing Guide](https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution)

---

**Created by: Osman Sabri Kiratli**

For questions or issues, please visit the [GitHub repository](https://github.com/okiratli/abc).

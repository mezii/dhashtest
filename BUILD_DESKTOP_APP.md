# dHash Face Recognition - Desktop App Build Guide

## 🖥️ Build Options

### **Option 1: PyWebView (Recommended - Lightweight)**
Creates a native window with your web app inside.

### **Option 2: PyInstaller (Standalone Executable)**
Bundles everything into a single .app (Mac) or .exe (Windows) file.

### **Option 3: Electron (Most Professional)**
Full-featured desktop app with native features.

---

## 🚀 Option 1: PyWebView (Easiest)

### Install Dependencies:
```bash
cd /Users/mins/Documents/MKApp/dhash
source .venv/bin/activate

# For Mac
pip install pywebview

# For Windows (if building on Windows)
pip install pywebview pywin32
```

### Run as Desktop App:
```bash
python desktop_app.py
```

### Build Standalone App:
```bash
# Install PyInstaller
pip install pyinstaller

# For Mac (.app)
pyinstaller --name="dHash Face Recognition" \
  --windowed \
  --onefile \
  --icon=icon.icns \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import=PIL \
  --hidden-import=cv2 \
  desktop_app.py

# For Windows (.exe)
pyinstaller --name="dHash Face Recognition" ^
  --windowed ^
  --onefile ^
  --icon=icon.ico ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import=PIL ^
  --hidden-import=cv2 ^
  desktop_app.py
```

Output: `dist/dHash Face Recognition.app` (Mac) or `dist/dHash Face Recognition.exe` (Windows)

---

## 📦 Option 2: PyInstaller Only (No Window Wrapper)

### Install:
```bash
pip install pyinstaller
```

### Create Launcher Script:
Create `launcher.py`:
```python
import webbrowser
import time
from app import app

if __name__ == '__main__':
    # Open browser after 2 seconds
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://127.0.0.1:5000')
    
    import threading
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Start Flask
    app.run(host='127.0.0.1', port=5000, debug=False)
```

### Build:
```bash
# Mac
pyinstaller --name="dHash" \
  --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  launcher.py

# Windows
pyinstaller --name="dHash" ^
  --onefile ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  launcher.py
```

---

## 🎨 Option 3: Electron (Most Professional)

### Setup:
```bash
# Install Node.js first (from nodejs.org)

# Create Electron wrapper
mkdir electron-app
cd electron-app
npm init -y
npm install electron electron-builder
```

### Create main.js:
```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');
const path = require('path');

let flaskProcess;
let mainWindow;

function startFlask() {
  flaskProcess = spawn('python', [
    path.join(__dirname, '..', 'app.py')
  ]);
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false
    }
  });

  setTimeout(() => {
    mainWindow.loadURL('http://127.0.0.1:5000');
  }, 2000);
}

app.whenReady().then(() => {
  startFlask();
  createWindow();
});

app.on('window-all-closed', () => {
  if (flaskProcess) flaskProcess.kill();
  app.quit();
});
```

### Build:
```bash
# Mac
npm run build -- --mac

# Windows
npm run build -- --win

# Both
npm run build -- --mac --win
```

---

## 🎯 Recommended Approach: PyWebView + PyInstaller

This gives you:
✅ Native window appearance
✅ Small file size (~50MB)
✅ Cross-platform (Mac/Windows)
✅ Easy to build

### Complete Build Commands:

**For Mac:**
```bash
cd /Users/mins/Documents/MKApp/dhash
source .venv/bin/activate

# Install dependencies
pip install pywebview pyinstaller

# Build
pyinstaller --name="dHash Face Recognition" \
  --windowed \
  --onefile \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import=PIL._imaging \
  --hidden-import=cv2 \
  --hidden-import=imagehash \
  --hidden-import=numpy \
  --collect-all imagehash \
  --collect-all cv2 \
  desktop_app.py

# Find your app in:
# dist/dHash Face Recognition.app
```

**For Windows (run on Windows machine):**
```cmd
cd dhash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install pywebview pyinstaller

pyinstaller --name="dHash Face Recognition" ^
  --windowed ^
  --onefile ^
  --add-data "templates;templates" ^
  --add-data "static;static" ^
  --hidden-import=PIL._imaging ^
  --hidden-import=cv2 ^
  --hidden-import=imagehash ^
  --hidden-import=numpy ^
  --collect-all imagehash ^
  --collect-all cv2 ^
  desktop_app.py
```

---

## 📝 Update requirements.txt:

Add to requirements.txt:
```
pywebview>=4.0
pyinstaller>=6.0
```

---

## 🎨 Create App Icon (Optional)

### For Mac (.icns):
1. Create a 1024x1024 PNG icon
2. Use online converter: cloudconvert.com (PNG to ICNS)
3. Save as `icon.icns`
4. Add `--icon=icon.icns` to pyinstaller command

### For Windows (.ico):
1. Create a 256x256 PNG icon
2. Use online converter: cloudconvert.com (PNG to ICO)
3. Save as `icon.ico`
4. Add `--icon=icon.ico` to pyinstaller command

---

## 🚀 Quick Start (Mac):

```bash
cd /Users/mins/Documents/MKApp/dhash
source .venv/bin/activate
pip install pywebview pyinstaller
python desktop_app.py
```

This will launch a desktop window with your app!

---

## 📦 Distribution:

### Mac:
- **File**: `dist/dHash Face Recognition.app`
- **Size**: ~50-100MB
- **Share**: Zip the .app file or create DMG

### Windows:
- **File**: `dist/dHash Face Recognition.exe`
- **Size**: ~50-100MB
- **Share**: Create installer with Inno Setup

---

## ⚠️ Code Signing (For Distribution):

### Mac:
```bash
# Sign the app (requires Apple Developer account)
codesign --deep --force --verify --verbose \
  --sign "Developer ID Application: Your Name" \
  "dist/dHash Face Recognition.app"

# Notarize (for macOS Gatekeeper)
xcrun notarytool submit "dHash.zip" \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "TEAM_ID"
```

### Windows:
- Use a code signing certificate
- Sign with SignTool.exe

---

## 🎉 Result:

Users can:
1. Download the app
2. Double-click to run
3. No installation needed
4. Works offline
5. Native desktop experience!

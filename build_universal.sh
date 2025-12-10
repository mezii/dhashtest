#!/bin/bash
# Build Universal Mac app (works on both Intel and ARM Macs)

cd /Users/mins/Documents/MKApp/dhash
source .venv/bin/activate

echo "🔨 Building Universal Mac App (Intel + ARM)..."
echo "This may take 2-3 minutes..."

pyinstaller --clean --noconfirm \
  --name="dHash Face Recognition Universal" \
  --windowed \
  --target-arch universal2 \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import=PIL._imaging \
  --hidden-import=cv2 \
  --hidden-import=imagehash \
  --hidden-import=numpy \
  --collect-all imagehash \
  --collect-all cv2 \
  desktop_app.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build complete!"
    echo "📦 Universal app: dist/dHash Face Recognition Universal.app"
    echo ""
    echo "Creating zip file..."
    cd dist
    
    if [ -d "dHash Face Recognition Universal.app" ]; then
        zip -r "dHash-Universal-MacOS.zip" "dHash Face Recognition Universal.app"
        echo "✅ Created: dHash-Universal-MacOS.zip"
    fi
    
    echo ""
    echo "🎉 Done!"
    echo ""
    echo "This app works on:"
    echo "  ✅ Intel Macs (x86_64)"
    echo "  ✅ Apple Silicon Macs (ARM64 - M1/M2/M3)"
else
    echo ""
    echo "❌ Build failed!"
fi

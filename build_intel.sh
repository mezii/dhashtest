#!/bin/bash
# Build Mac Intel (x86_64) version

cd /Users/mins/Documents/MKApp/dhash
source .venv/bin/activate

echo "🔨 Building dHash for Mac Intel (x86_64)..."
echo "This may take 2-3 minutes..."

pyinstaller --clean --noconfirm \
  --name="dHash Face Recognition Intel" \
  --windowed \
  --target-arch x86_64 \
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
    echo "📦 Intel app location: dist/dHash Face Recognition Intel.app"
    echo "📦 ARM app location: dist/dHash Face Recognition.app"
    echo ""
    echo "Creating zip files..."
    cd dist
    
    # Zip Intel version
    if [ -d "dHash Face Recognition Intel.app" ]; then
        zip -r "dHash-Intel-x86_64.zip" "dHash Face Recognition Intel.app"
        echo "✅ Created: dHash-Intel-x86_64.zip"
    fi
    
    echo ""
    echo "🎉 Done!"
    echo ""
    echo "You now have:"
    echo "  - ARM (M1/M2/M3): dHash Face Recognition.app"
    echo "  - Intel: dHash Face Recognition Intel.app"
else
    echo ""
    echo "❌ Build failed!"
fi

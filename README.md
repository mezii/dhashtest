# Face Image Comparison Tool with dHash

A web-based application to compare two face images using the dHash (Difference Hash) algorithm. The tool provides a visual interface to upload images and displays similarity results.

## Features

- 🖼️ **Drag & Drop Upload**: Easy image upload with drag-and-drop support
- 🔍 **dHash Algorithm**: Uses perceptual hashing for robust image comparison
- 📊 **Visual Results**: Shows similarity percentage and Hamming distance
- 🎨 **Modern UI**: Clean, responsive web interface
- ⚡ **Fast Processing**: Quick comparison results

## How dHash Works

dHash (Difference Hash) is a perceptual hashing algorithm that:
1. Resizes the image to a small size (typically 9x8 pixels)
2. Converts to grayscale
3. Compares adjacent pixels to create a binary hash
4. The resulting 64-bit hash can be compared using Hamming distance

Images are considered similar when they have ≥90% similarity (Hamming distance ≤ 6 bits).

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload two images by:
   - Clicking on the upload boxes
   - Or dragging and dropping images

4. Click "Compare Images" to see the results

## Technical Details

- **Backend**: Flask (Python)
- **Image Processing**: Pillow (PIL)
- **Hash Algorithm**: ImageHash library (dHash)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3

## Project Structure

```
dhash/
├── app.py              # Flask application and comparison logic
├── requirements.txt    # Python dependencies
├── templates/
│   └── index.html     # Main UI template
└── static/
    ├── style.css      # Styling
    └── script.js      # Client-side logic
```

## Similarity Threshold

- **≥90%**: Images are considered matching (same face)
- **<90%**: Images are considered different

You can adjust this threshold in `app.py` by modifying the comparison logic.

## Supported Image Formats

- PNG
- JPG/JPEG
- Maximum file size: 16MB

## License

MIT License

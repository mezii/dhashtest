from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image, ImageEnhance
import imagehash
import cv2
import numpy as np
import hashlib
import io
import os
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def calculate_dhash(image_data):
    """Calculate dhash for an image"""
    try:
        image = Image.open(io.BytesIO(image_data))
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        # Calculate dhash
        hash_value = imagehash.dhash(image)
        return hash_value
    except Exception as e:
        print(f"Error calculating dhash: {e}")
        return None

def compare_images(image1_data, image2_data):
    """Compare two images using dhash"""
    hash1 = calculate_dhash(image1_data)
    hash2 = calculate_dhash(image2_data)
    
    if hash1 is None or hash2 is None:
        return None, None, None
    
    # Calculate Hamming distance (number of different bits)
    hamming_distance = hash1 - hash2
    
    # Calculate similarity percentage
    # dhash produces 64-bit hash, so max distance is 64
    max_distance = 64
    similarity = (1 - (hamming_distance / max_distance)) * 100
    
    # Determine if images are similar (threshold: 85% similarity for same person photos)
    are_similar = similarity >= 85
    
    return hamming_distance, similarity, are_similar

def calculate_perceptual_hash_cv(image_data):
    """Calculate perceptual hash using OpenCV"""
    nparr = np.frombuffer(image_data, np.uint8)
    image_cv_gray = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    image_resized = cv2.resize(image_cv_gray, (8, 8), interpolation=cv2.INTER_AREA)
    diff = image_resized[:, 1:] > image_resized[:, :-1]
    perceptual_hash = ''.join(['1' if v else '0' for v in diff.flatten()])
    perceptual_hash_hex = '{:0x}'.format(int(perceptual_hash, 2))
    return perceptual_hash_hex

def hamming_distance_hash(hash1, hash2):
    """Calculate Hamming distance between two hashes"""
    bin1 = bin(int(hash1, 16))[2:].zfill(64)
    bin2 = bin(int(hash2, 16))[2:].zfill(64)
    return sum(c1 != c2 for c1, c2 in zip(bin1, bin2))

def break_perceptual_hash(image_data, brightness_factor=0.85, gradient_factor=80):
    """
    Balanced modification to bypass detection while keeping image visible
    Defeats dHash and basic face recognition without destroying the image
    """
    # Load image with OpenCV
    nparr = np.frombuffer(image_data, np.uint8)
    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    height, width = img_cv.shape[:2]
    
    # Calculate original hash
    original_hash = calculate_perceptual_hash_cv(image_data)
    
    import random
    random.seed(42)
    
    # === PHASE 1: Subtle Pattern Overlay (breaks hash) ===
    
    # 1. Light diagonal lines (every 15 pixels - subtle but effective)
    for i in range(0, min(width, height), 15):
        if 0 <= i < width and 0 <= i < height:
            # Blend instead of overwrite
            b, g, r = img_cv[i, i]
            img_cv[i, i] = [min(b + 80, 255), min(g + 80, 255), min(r + 80, 255)]
        if 0 <= width - i - 1 < width and 0 <= i < height:
            b, g, r = img_cv[i, width - i - 1]
            img_cv[i, width - i - 1] = [min(b + 80, 255), min(g + 80, 255), min(r + 80, 255)]
    
    # 2. Moderate noise injection (±15 instead of ±40)
    noise = np.random.randint(-15, 16, img_cv.shape, dtype=np.int16)
    img_cv = np.clip(img_cv.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    
    # 3. Subtle texture grid (every 8 pixels)
    for y in range(0, height, 8):
        for x in range(0, width, 8):
            if (x + y) % 16 == 0:
                b, g, r = img_cv[y, x]
                img_cv[y, x] = [min(b + 10, 255), min(g + 10, 255), min(r + 10, 255)]
    
    # === PHASE 2: Color & Contrast Adjustments ===
    
    # 4. Slight color channel shift (every 30 pixels, less aggressive)
    for y in range(0, height, 30):
        for x in range(0, width, 30):
            if random.random() > 0.6:  # Only 40% of pixels
                b, g, r = img_cv[y, x]
                img_cv[y, x] = [r, b, g]
    
    # 5. Gentle contrast adjustment
    alpha = 1.15  # Slight contrast increase
    beta = 10     # Slight brightness increase
    img_cv = cv2.convertScaleAbs(img_cv, alpha=alpha, beta=beta)
    
    # 6. Add subtle adversarial pattern (every 4 pixels, small perturbation)
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            perturbation = 8 if (x + y) % 8 == 0 else -8
            img_cv[y, x] = np.clip(img_cv[y, x].astype(np.int16) + perturbation, 0, 255).astype(np.uint8)
    
    # === PHASE 3: Edge & Frequency Modifications ===
    
    # 7. Very light blur then mild sharpen
    img_cv = cv2.GaussianBlur(img_cv, (3, 3), 0)
    kernel_sharpen = np.array([[0,-1,0], [-1,5,-1], [0,-1,0]])  # Milder sharpening
    img_cv = cv2.filter2D(img_cv, -1, kernel_sharpen)
    
    # 8. Add faint grid overlay (every 25 pixels)
    overlay = np.zeros_like(img_cv)
    for y in range(0, height, 25):
        cv2.line(overlay, (0, y), (width, y), (50, 50, 50), 1)
    for x in range(0, width, 25):
        cv2.line(overlay, (x, 0), (x, height), (50, 50, 50), 1)
    img_cv = cv2.addWeighted(img_cv, 0.95, overlay, 0.05, 0)  # Only 5% overlay
    
    # 9. Minor perspective distortion (2-5 pixels only)
    rows, cols = img_cv.shape[:2]
    src_points = np.float32([[0, 0], [cols-1, 0], [0, rows-1], [cols-1, rows-1]])
    dst_points = np.float32([
        [random.randint(0, 3), random.randint(0, 3)],
        [cols-1-random.randint(0, 3), random.randint(0, 3)],
        [random.randint(0, 3), rows-1-random.randint(0, 3)],
        [cols-1-random.randint(0, 3), rows-1-random.randint(0, 3)]
    ])
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    img_cv = cv2.warpPerspective(img_cv, matrix, (cols, rows))
    
    # 10. Subtle color cast (±8 instead of ±20)
    color_cast = np.full(img_cv.shape, [random.randint(-8, 9), 
                                         random.randint(-8, 9), 
                                         random.randint(-8, 9)], dtype=np.int16)
    img_cv = np.clip(img_cv.astype(np.int16) + color_cast, 0, 255).astype(np.uint8)
    
    # Convert back to PIL for final adjustments
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    image = Image.fromarray(img_rgb)
    
    # 11. Gentle brightness/contrast/color adjustments
    image = ImageEnhance.Brightness(image).enhance(brightness_factor)  # 0.85 = slight darkening
    image = ImageEnhance.Contrast(image).enhance(1.05)  # Slight contrast boost
    image = ImageEnhance.Color(image).enhance(1.1)  # Slight saturation boost
    
    # Save to bytes
    output = io.BytesIO()
    image.save(output, format='PNG')
    output.seek(0)
    modified_data = output.getvalue()
    
    # Calculate new hash
    new_hash = calculate_perceptual_hash_cv(modified_data)
    hamming_dist = hamming_distance_hash(original_hash, new_hash)
    
    return modified_data, original_hash, new_hash, hamming_dist

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/compare', methods=['POST'])
def compare():
    """Compare two uploaded images"""
    try:
        print("=== Compare endpoint called ===")
        print(f"Request files: {request.files}")
        
        # Check if both images are present
        if 'image1' not in request.files or 'image2' not in request.files:
            print("Error: Both images not present in request")
            return jsonify({'error': 'Both images are required'}), 400
        
        file1 = request.files['image1']
        file2 = request.files['image2']
        
        print(f"File1: {file1.filename}, File2: {file2.filename}")
        
        if file1.filename == '' or file2.filename == '':
            print("Error: One or both filenames are empty")
            return jsonify({'error': 'Both images must be selected'}), 400
        
        # Read image data
        image1_data = file1.read()
        image2_data = file2.read()
        
        print(f"Image1 size: {len(image1_data)} bytes, Image2 size: {len(image2_data)} bytes")
        
        # Compare images using dHash
        hamming_distance, similarity, are_similar = compare_images(image1_data, image2_data)
        
        print(f"Comparison result - Hamming: {hamming_distance}, Similarity: {similarity}, Similar: {are_similar}")
        
        if hamming_distance is None:
            return jsonify({'error': 'Failed to process images'}), 400
        
        # Prepare response
        response = {
            'hamming_distance': int(hamming_distance),
            'similarity': round(float(similarity), 2),
            'are_similar': bool(are_similar),
            'message': 'Same person!' if are_similar else 'Different person.'
        }
        
        return jsonify(response)
    
    except Exception as e:
        print(f"=== ERROR in compare endpoint ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/anti-dhash', methods=['POST'])
def anti_dhash():
    """Modify an image to bypass dhash detection"""
    try:
        print("=== Anti-dHash endpoint called ===")
        
        # Check if image is present
        if 'image' not in request.files:
            return jsonify({'error': 'Image is required'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Read image data
        image_data = file.read()
        print(f"Processing image: {file.filename}, size: {len(image_data)} bytes")
        
        # Apply anti-dhash modifications
        modified_data, original_hash, new_hash, hamming_dist = break_perceptual_hash(image_data)
        
        print(f"Original hash: {original_hash}")
        print(f"New hash: {new_hash}")
        print(f"Hamming distance: {hamming_dist}")
        
        # Prepare response with modified image
        response = {
            'success': True,
            'original_hash': original_hash,
            'new_hash': new_hash,
            'hamming_distance': hamming_dist,
            'message': f'Image modified! Hamming distance: {hamming_dist} bits'
        }
        
        # Store modified image temporarily for download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f'modified_{timestamp}.png'
        temp_path = os.path.join('static', 'temp', temp_filename)
        os.makedirs(os.path.dirname(temp_path), exist_ok=True)
        
        with open(temp_path, 'wb') as f:
            f.write(modified_data)
        
        response['download_url'] = f'/download/{temp_filename}'
        
        return jsonify(response)
    
    except Exception as e:
        print(f"=== ERROR in anti-dhash endpoint ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Download modified image"""
    try:
        file_path = os.path.join('static', 'temp', filename)
        return send_file(file_path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 404

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    os.makedirs('static/temp', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

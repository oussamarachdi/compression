from flask import Flask, request, jsonify
from PIL import Image
import os



app = Flask(__name__)

def compress_to_webp(image_path, output_path):
    with Image.open(image_path) as img:
        # Save image in WebP format with lossless compression
        img.save(output_path, 'WEBP', lossless=True)

def decompress_webp(webp_path, output_path):
    with Image.open(webp_path) as img:
        # Save decompressed image (in original format)
        img.save(output_path)


@app.route('/compress_webp', methods=['POST'])
def compress_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        # Save the uploaded image temporarily
        image_path = 'temp_original.jpg'
        file.save(image_path)

        # Compress the image to WebP
        compressed_path = 'temp_compressed.webp'
        compress_to_webp(image_path, compressed_path)

        # Read the compressed image
        with open(compressed_path, 'rb') as compressed_file:
            compressed_data = compressed_file.read()

        return compressed_data, 200, {'Content-Type': 'image/webp', 'Content-Disposition': 'inline; filename=compressed.webp'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

    finally:
        # Clean up temporary files
        if 'image_path' in locals() and os.path.exists(image_path):
            os.remove(image_path)
        if 'compressed_path' in locals() and os.path.exists(compressed_path):
            os.remove(compressed_path)

if __name__ == '__main__':
    app.run(debug=True)
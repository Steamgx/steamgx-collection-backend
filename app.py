from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

ITEMS_FILE = os.path.join(os.path.dirname(__file__), 'items.json')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ADMIN_PASSWORD = '0769998718bM_'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Helper to load items
def load_items():
    if not os.path.exists(ITEMS_FILE):
        return []
    with open(ITEMS_FILE, 'r') as f:
        return json.load(f)

# Helper to save items
def save_items(items):
    with open(ITEMS_FILE, 'w') as f:
        json.dump(items, f, indent=2)

# Get all items
@app.route('/api/items', methods=['GET'])
def get_items():
    items = load_items()
    return jsonify(items)

# Add a new item (admin only)
@app.route('/api/items', methods=['POST'])
def add_item():
    data = request.json
    password = data.get('password')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401
    item = {
        'id': data.get('id'),
        'name': data.get('name'),
        'description': data.get('description'),
        'price': data.get('price'),
        'category': data.get('category'),
        'image': data.get('image'),
    }
    items = load_items()
    item['id'] = len(items) + 1
    items.append(item)
    save_items(items)
    return jsonify({'success': True, 'item': item})

# (Optional) Delete item (admin only)
@app.route('/api/items/<int:item_id>', methods=['DELETE'])
def delete_item(item_id):
    data = request.json
    password = data.get('password')
    if password != ADMIN_PASSWORD:
        return jsonify({'error': 'Unauthorized'}), 401
    items = load_items()
    items = [item for item in items if item['id'] != item_id]
    save_items(items)
    return jsonify({'success': True})

# Image upload endpoint
@app.route('/api/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        save_path = os.path.join(UPLOAD_FOLDER, filename)
        # Ensure unique filename
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(save_path):
            filename = f"{base}_{counter}{ext}"
            save_path = os.path.join(UPLOAD_FOLDER, filename)
            counter += 1
        file.save(save_path)
        url = f"/uploads/{filename}"
        return jsonify({'url': url, 'filename': filename})
    return jsonify({'error': 'Invalid file type'}), 400

# Serve uploaded images
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 
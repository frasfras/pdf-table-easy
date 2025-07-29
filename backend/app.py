from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import fitz
from PIL import Image
import io

from paddleocr import PPStructure, save_structure_res

app = Flask(__name__)

# Replace with your actual deployed frontend URL
CORS(app, resources={r"/*": {"origins": "https://stellular-hotteok.netlify.app/"}})
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Table extraction model
ocr = PPStructure(layout=True)  # structure=True is not valid in PaddleOCR

@app.route('/extract', methods=['POST'])
def extract_tables():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    doc = fitz.open(filepath)
    all_tables = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=200)
        image_bytes = pix.tobytes("png")
        image = Image.open(io.BytesIO(image_bytes))

        result = ocr(image)
        for region in result:
            if region['type'] == 'table':
                rows = []
                for row in region['res']:
                    cells = [c for c in row if c.strip()]
                    if cells:
                        rows.append(cells)
                if rows:
                    all_tables.append({
                        'page': page_num + 1,
                        'rows': rows
                    })

    return jsonify({'tables': all_tables})

if __name__ == '__main__':
    app.run(debug=True)

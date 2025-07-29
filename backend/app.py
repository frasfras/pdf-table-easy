from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import fitz  # PyMuPDF
from PIL import Image
import io
from paddleocr import PaddleOCR


app = Flask(__name__)

# Replace with your actual deployed frontend URL
CORS(app, resources={r"/*": {"origins": "https://stellular-hotteok.netlify.app/"}})

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Use structure=True to enable layout analysis (table detection)
ocr = PaddleOCR(use_angle_cls=True, lang='en', structure=True, show_log=False)

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

        # Run layout analysis
        result = ocr.ocr(image, det=True, rec=True, structure=True, cls=True)

        rows = []
        for element in result:
            if element['type'] == 'table':
                for row in element['res']:
                    cell_values = [cell.strip() for cell in row if isinstance(cell, str) and cell.strip()]
                    if cell_values:
                        rows.append(cell_values)

        if rows:
            all_tables.append({
                'page': page_num + 1,
                'rows': rows
            })

    return jsonify({'tables': all_tables})

if __name__ == '__main__':
    app.run(debug=True)

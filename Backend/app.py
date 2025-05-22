from flask import Flask, request, send_from_directory, jsonify, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ✅ Tambahkan ini!
data_list = []

@app.route('/')
def index():
    return render_template('index.html', data=data_list)


@app.route('/')
def index():
    return render_template('index.html', data=data_list)

@app.route('/kirim', methods=['POST'])
def kirim():
    teks = request.form.get('teks', '')
    gambar = request.files.get('gambar')
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    entry = {'teks': teks, 'gambar': None, 'timestamp': timestamp}

    if gambar:
        filename = f"{timestamp}_{secure_filename(gambar.filename)}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        gambar.save(filepath)
        entry['gambar'] = filename

    data_list.append(entry)
    return 'Data diterima'

@app.route('/data')
def get_data():
    return jsonify(data_list)

@app.route('/uploads/<filename>')
def get_gambar(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

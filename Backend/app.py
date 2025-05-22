from flask import Flask, request, send_from_directory, jsonify, render_template, send_file, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import io
import zipfile

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

@app.route('/download/teks/<timestamp>')
def download_teks(timestamp):
    for entry in data_list:
        if entry['timestamp'] == timestamp and entry['teks']:
            teks = entry['teks']
            return send_file(
                io.BytesIO(teks.encode()),
                as_attachment=True,
                download_name=f"{timestamp}_teks.txt",
                mimetype='text/plain'
            )
    return 'Teks tidak ditemukan', 404

@app.route('/download/gambar/<filename>')
def download_gambar(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return 'Gambar tidak ditemukan', 404

@app.route('/download/zip/<timestamp>')
def download_zip(timestamp):
    for entry in data_list:
        if entry['timestamp'] == timestamp:
            zip_io = io.BytesIO()
            with zipfile.ZipFile(zip_io, 'w') as zf:
                if entry['teks']:
                    zf.writestr(f"{timestamp}_teks.txt", entry['teks'])
                if entry['gambar']:
                    img_path = os.path.join(app.config['UPLOAD_FOLDER'], entry['gambar'])
                    if os.path.exists(img_path):
                        zf.write(img_path, arcname=entry['gambar'])
            zip_io.seek(0)
            return send_file(zip_io, as_attachment=True, download_name=f"{timestamp}_data.zip", mimetype='application/zip')
    return 'Data tidak ditemukan', 404

@app.route('/hapus/<timestamp>', methods=['POST'])
def hapus(timestamp):
    global data_list
    new_data = []
    for entry in data_list:
        if entry['timestamp'] == timestamp:
            if entry['gambar']:
                try:
                    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], entry['gambar']))
                except FileNotFoundError:
                    pass
        else:
            new_data.append(entry)
    data_list = new_data
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

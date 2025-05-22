from flask import Flask, request, send_from_directory, jsonify, render_template, send_file, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import io

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
    for item in data_list:
        if item['timestamp'] == timestamp:
            teks = item['teks'] or '(tidak ada teks)'
            return send_file(
                io.BytesIO(teks.encode()),
                download_name=f'teks_{timestamp}.txt',
                as_attachment=True,
                mimetype='text/plain'
            )
    return 'Data tidak ditemukan', 404

@app.route('/download/semua/<timestamp>')
def download_semua(timestamp):
    for item in data_list:
        if item['timestamp'] == timestamp:
            mem_zip = io.BytesIO()
            with zipfile.ZipFile(mem_zip, 'w') as zipf:
                teks = item['teks'] or '(tidak ada teks)'
                zipf.writestr(f'teks_{timestamp}.txt', teks)
                if item['gambar']:
                    path_gambar = os.path.join(app.config['UPLOAD_FOLDER'], item['gambar'])
                    zipf.write(path_gambar, arcname=item['gambar'])

            mem_zip.seek(0)
            return send_file(
                mem_zip,
                download_name=f'data_{timestamp}.zip',
                as_attachment=True,
                mimetype='application/zip'
            )
    return 'Data tidak ditemukan', 404

@app.route('/hapus/<timestamp>', methods=['POST'])
def hapus(timestamp):
    global data_list
    for item in data_list:
        if item['timestamp'] == timestamp:
            if item['gambar']:
                path_gambar = os.path.join(app.config['UPLOAD_FOLDER'], item['gambar'])
                if os.path.exists(path_gambar):
                    os.remove(path_gambar)
            data_list = [d for d in data_list if d['timestamp'] != timestamp]
            break
    return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

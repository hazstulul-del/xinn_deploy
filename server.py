#!/usr/bin/env python3
"""
XINN DEPLOY V4 - SIMPLE VERSION
Simpan file langsung di server, tampilkan instan.
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import uuid
from datetime import datetime

app = Flask(__name__)

# Buat folder utama untuk menyimpan file yang di-deploy
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'deployed_sites')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# HTML Template (Langsung dari sini aja biar ga ribet)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XINN DEPLOY V4 - Deploy Website Gratis</title>
    <style>
        :root {
            --bg: #0d1117; --card: #161b22; --border: #30363d;
            --accent: #58a6ff; --green: #3fb950; --text: #c9d1d9;
            --text2: #8b949e; --danger: #f85149;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif; background: var(--bg);
            color: var(--text); min-height: 100vh;
            padding: 20px;
            background-image:
                radial-gradient(ellipse at 20% 50%, rgba(88,166,255,0.05) 0%, transparent 70%),
                radial-gradient(ellipse at 80% 20%, rgba(63,185,80,0.05) 0%, transparent 70%);
        }
        .container { max-width: 700px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 24px; }
        .header-badge {
            display: inline-block; background: rgba(88,166,255,0.1);
            border: 1px solid rgba(88,166,255,0.3); color: var(--accent);
            padding: 6px 16px; border-radius: 20px; font-size: 0.8rem;
            letter-spacing: 1px; margin-bottom: 10px;
        }
        .header h1 {
            font-size: 2.5rem; font-weight: 700;
            background: linear-gradient(135deg, #58a6ff, #3fb950);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header .by { color: var(--text2); font-size: 0.9rem; }
        .header .by span { color: var(--accent); font-weight: 600; }
        .banner {
            border-radius: 12px; overflow: hidden; margin-bottom: 24px;
            border: 2px solid var(--border); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }
        .banner img { width: 100%; display: block; }
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 24px; margin-bottom: 16px;
        }
        .card-title {
            font-size: 1.1rem; font-weight: 600; margin-bottom: 20px;
            display: flex; align-items: center; gap: 10px;
        }
        .card-title .icon {
            width: 30px; height: 30px; background: rgba(88,166,255,0.15);
            border-radius: 8px; display: flex; align-items: center;
            justify-content: center; font-size: 1rem;
        }
        .form-group { margin-bottom: 18px; }
        .form-group label {
            display: block; font-size: 0.85rem; font-weight: 500;
            margin-bottom: 6px; color: var(--text2);
        }
        .form-group input[type="text"] {
            width: 100%; padding: 12px 16px; background: var(--bg);
            border: 1px solid var(--border); border-radius: 8px;
            color: var(--text); font-size: 0.95rem; outline: none; font-family: inherit;
        }
        .form-group input[type="text"]:focus {
            border-color: var(--accent); box-shadow: 0 0 0 3px rgba(88,166,255,0.1);
        }
        .file-upload { position: relative; }
        .file-upload input[type="file"] {
            position: absolute; width: 100%; height: 100%;
            opacity: 0; cursor: pointer; z-index: 2;
        }
        .file-upload-label {
            display: flex; align-items: center; gap: 10px;
            padding: 14px 18px; background: var(--bg);
            border: 2px dashed var(--border); border-radius: 8px;
            cursor: pointer; justify-content: center; font-size: 0.9rem;
        }
        .file-upload-label:hover { border-color: var(--accent); }
        .btn-deploy {
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, #238636, #2ea043);
            border: none; border-radius: 8px; color: #fff;
            font-size: 1rem; font-weight: 600; cursor: pointer;
            font-family: inherit; transition: 0.2s; margin-top: 6px;
        }
        .btn-deploy:hover { box-shadow: 0 6px 24px rgba(63,185,80,0.3); }
        .btn-deploy:disabled { opacity: 0.5; cursor: not-allowed; }
        .spinner {
            display: inline-block; width: 16px; height: 16px;
            border: 2px solid #fff; border-radius: 50%;
            border-top-color: transparent; animation: spin 0.6s linear infinite;
            margin-right: 8px; vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .result {
            border-radius: 8px; padding: 14px; display: none; margin-top: 14px;
            text-align: center; font-size: 0.9rem; animation: fadeIn 0.3s ease;
        }
        .result.show { display: block; }
        .result.success { background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.4); color: var(--green); }
        .result.error { background: rgba(248,81,73,0.1); border: 1px solid rgba(248,81,73,0.4); color: var(--danger); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
        .rules {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 16px 20px; margin-top: 16px;
        }
        .rules h4 { font-size: 0.85rem; margin-bottom: 10px; }
        .rules ul { list-style: none; font-size: 0.8rem; color: var(--text2); }
        .rules ul li { padding: 4px 0; display: flex; align-items: flex-start; gap: 6px; }
        .rules ul li::before { content: "•"; color: var(--accent); }
        .contact { display: flex; gap: 12px; margin-top: 20px; flex-wrap: wrap; }
        .contact-btn {
            flex: 1; min-width: 140px; display: flex; align-items: center;
            justify-content: center; gap: 8px; padding: 12px;
            border-radius: 8px; text-decoration: none; font-size: 0.9rem;
            font-weight: 500; border: 1px solid var(--border);
        }
        .contact-btn.wa { background: rgba(37,211,102,0.1); color: #25d366; border-color: rgba(37,211,102,0.3); }
        .contact-btn.tg { background: rgba(0,136,204,0.1); color: #0088cc; border-color: rgba(0,136,204,0.3); }
        .footer-text { text-align: center; margin-top: 20px; font-size: 0.75rem; color: var(--text2); }
        .footer-text span { color: var(--accent); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-badge">🚀 DEPLOY GRATIS V4</div>
            <h1>XINN DEPLOY</h1>
            <p class="by">Deploy Website by <span>XINN</span></p>
        </div>
        <div class="banner">
            <img src="{{ url_for('static', filename='img/banner.gif') }}" alt="Banner">
        </div>
        <div class="card">
            <div class="card-title">
                <span class="icon">📄</span> Upload File HTML
            </div>
            <form id="deployForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Nama Website</label>
                    <input type="text" name="site_name" id="siteName" placeholder="contoh: webku-by-xinn" maxlength="30" required>
                </div>
                <div class="form-group">
                    <label>Upload File HTML</label>
                    <div class="file-upload">
                        <input type="file" name="html_file" id="fileInput" accept=".html,.htm" required>
                        <div class="file-upload-label">
                            <span>📁</span>
                            <span id="uploadText">Pilih File HTML</span>
                        </div>
                    </div>
                    <div class="file-name" id="fileName">Tidak ada file yang dipilih</div>
                </div>
                <button type="submit" class="btn-deploy" id="deployBtn">🚀 Deploy Sekarang</button>
            </form>
            <div class="result" id="resultBox">
                <div id="resultIcon"></div>
                <span id="resultTitle"></span>
                <div id="resultMsg" style="font-size:0.8rem; margin-top:6px;"></div>
            </div>
        </div>
        <div class="rules">
            <h4>📌 Syarat & Ketentuan</h4>
            <ul>
                <li>File wajib bernama <strong>index.html</strong>.</li>
                <li>Tidak boleh mengandung konten ilegal.</li>
                <li>Website bersifat <strong>publik & gratis</strong>.</li>
                <li>Maksimal ukuran file: <strong>2 MB</strong>.</li>
            </ul>
        </div>
        <div class="contact">
            <a href="https://wa.me/6283175050030" target="_blank" class="contact-btn wa">
                💬 WhatsApp – 083175050030
            </a>
            <a href="https://t.me/xinn_93" target="_blank" class="contact-btn tg">
                ✈️ Telegram – @xinn_93
            </a>
        </div>
        <p class="footer-text">Credit by <span>XINN</span> • Deploy Website Gratis © 2024 • V4</p>
    </div>
    <script>
        const fileInput = document.getElementById("fileInput");
        const uploadText = document.getElementById("uploadText");
        const fileName = document.getElementById("fileName");
        fileInput.addEventListener("change", function() {
            if (this.files.length > 0) {
                uploadText.textContent = this.files[0].name;
                fileName.textContent = "✅ " + this.files[0].name;
                fileName.style.color = "#3fb950";
            } else {
                uploadText.textContent = "Pilih File HTML";
                fileName.textContent = "Tidak ada file yang dipilih";
                fileName.style.color = "#8b949e";
            }
        });
        document.getElementById("deployForm").addEventListener("submit", async function(e) {
            e.preventDefault();
            const btn = document.getElementById("deployBtn");
            const resultBox = document.getElementById("resultBox");
            const resultIcon = document.getElementById("resultIcon");
            const resultTitle = document.getElementById("resultTitle");
            const resultMsg = document.getElementById("resultMsg");
            resultBox.className = "result";
            resultBox.style.display = "none";
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Deploying...';
            const formData = new FormData(this);
            try {
                const response = await fetch("/deploy", { method: "POST", body: formData });
                const data = await response.json();
                if (data.status === "success") {
                    resultBox.classList.add("show", "success");
                    resultIcon.textContent = "✅";
                    resultTitle.innerHTML = '<a href="' + data.url + '" target="_blank" style="color:#3fb950;">' + data.url + '</a>';
                    resultMsg.textContent = 'Website berhasil dideploy!';
                    document.getElementById("deployForm").reset();
                    uploadText.textContent = "Pilih File HTML";
                    fileName.textContent = "Tidak ada file yang dipilih";
                    fileName.style.color = "#8b949e";
                } else {
                    resultBox.classList.add("show", "error");
                    resultIcon.textContent = "❌";
                    resultTitle.textContent = data.message;
                }
            } catch (err) {
                resultBox.classList.add("show", "error");
                resultIcon.textContent = "❌";
                resultTitle.textContent = "Gagal terhubung ke server.";
            }
            btn.disabled = false;
            btn.innerHTML = "🚀 Deploy Sekarang";
        });
    </script>
</body>
</html>
'''

# ==================== ROUTES ====================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/deploy', methods=['POST'])
def deploy():
    site_name = request.form.get('site_name', '').strip()
    if not site_name:
        return jsonify({'status': 'error', 'message': 'Nama website wajib diisi!'})
    
    # Sanitasi nama
    safe_name = ''.join(c for c in site_name if c.isalnum() or c in '-_')
    if len(safe_name) < 3:
        return jsonify({'status': 'error', 'message': 'Nama minimal 3 karakter!'})
    
    if 'html_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'File HTML wajib diupload!'})
    
    file = request.files['html_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'File tidak boleh kosong!'})
    
    # Bikin folder untuk user ini
    user_folder = os.path.join(UPLOAD_FOLDER, safe_name)
    os.makedirs(user_folder, exist_ok=True)
    
    # Simpan file
    file_path = os.path.join(user_folder, 'index.html')
    file.save(file_path)
    
    # Generate URL
    base_url = request.host_url.rstrip('/')
    public_url = f"{base_url}/site/{safe_name}"
    
    return jsonify({
        'status': 'success',
        'message': f'Website "{safe_name}" berhasil dideploy!',
        'url': public_url
    })

@app.route('/site/<site_name>')
def serve_site(site_name):
    safe_name = ''.join(c for c in site_name if c.isalnum() or c in '-_')
    user_folder = os.path.join(UPLOAD_FOLDER, safe_name)
    
    if os.path.exists(os.path.join(user_folder, 'index.html')):
        return send_from_directory(user_folder, 'index.html')
    else:
        return "Website tidak ditemukan. <a href='/'>Kembali</a>", 404

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

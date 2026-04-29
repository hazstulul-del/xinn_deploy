#!/usr/bin/env python3
"""
XINN DEPLOY - Backend Flask untuk Railway
Banner: static/img/banner.gif (file lokal dari repo)
"""

from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# Folder deploy
UPLOAD_FOLDER = '/tmp/deployed_sites'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Folder static/img buat banner.gif
STATIC_IMG = os.path.join(os.path.dirname(__file__), 'static', 'img')
os.makedirs(STATIC_IMG, exist_ok=True)

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XINN DEPLOY - Deploy Website Gratis</title>
    <style>
        :root {
            --bg: #0d1117; --card: #161b22; --border: #30363d;
            --accent: #58a6ff; --green: #3fb950; --text: #c9d1d9;
            --text2: #8b949e;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif; background: var(--bg);
            color: var(--text); min-height: 100vh; display: flex;
            justify-content: center; align-items: center; padding: 20px;
            background-image:
                radial-gradient(ellipse at 20% 50%, rgba(88,166,255,0.05) 0%, transparent 70%),
                radial-gradient(ellipse at 80% 20%, rgba(63,185,80,0.05) 0%, transparent 70%);
        }
        .container { width: 100%; max-width: 500px; }
        .header { text-align: center; margin-bottom: 20px; }
        .header-badge {
            display: inline-block; background: rgba(88,166,255,0.1);
            border: 1px solid rgba(88,166,255,0.3); color: var(--accent);
            padding: 6px 16px; border-radius: 20px; font-size: 0.8rem;
            letter-spacing: 1px; margin-bottom: 10px;
        }
        .header h1 {
            font-size: 2rem; font-weight: 700;
            background: linear-gradient(135deg, #58a6ff, #3fb950);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header .by { color: var(--text2); font-size: 0.9rem; }
        .header .by span { color: var(--accent); font-weight: 600; }
        .banner {
            border-radius: 12px; overflow: hidden; margin-bottom: 20px;
            border: 2px solid var(--border); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
        }
        .banner img { width: 100%; display: block; }
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 24px; margin-bottom: 16px;
        }
        .card-title {
            font-size: 1rem; font-weight: 600; margin-bottom: 16px;
            display: flex; align-items: center; gap: 8px;
        }
        .card-title .icon {
            width: 28px; height: 28px; background: rgba(88,166,255,0.15);
            border-radius: 6px; display: flex; align-items: center;
            justify-content: center; font-size: 0.9rem;
        }
        .form-group { margin-bottom: 16px; }
        .form-group label {
            display: block; font-size: 0.85rem; font-weight: 500;
            margin-bottom: 6px; color: var(--text2);
        }
        .form-group input[type="text"] {
            width: 100%; padding: 10px 14px; background: var(--bg);
            border: 1px solid var(--border); border-radius: 8px;
            color: var(--text); font-size: 0.9rem; outline: none; font-family: inherit;
        }
        .form-group input[type="text"]:focus {
            border-color: var(--accent); box-shadow: 0 0 0 3px rgba(88,166,255,0.1);
        }
        .form-group input[type="text"]::placeholder { color: #484f58; }
        .file-upload { position: relative; }
        .file-upload input[type="file"] {
            position: absolute; width: 100%; height: 100%;
            opacity: 0; cursor: pointer; z-index: 2;
        }
        .file-upload-label {
            display: flex; align-items: center; gap: 10px;
            padding: 14px 16px; background: var(--bg);
            border: 2px dashed var(--border); border-radius: 8px;
            cursor: pointer; justify-content: center; transition: 0.2s;
        }
        .file-upload-label:hover { border-color: var(--accent); }
        .file-name {
            font-size: 0.85rem; color: var(--text2);
            margin-top: 6px; text-align: center; word-break: break-all;
        }
        .btn-deploy {
            width: 100%; padding: 14px;
            background: linear-gradient(135deg, #238636, #2ea043);
            border: none; border-radius: 8px; color: #fff;
            font-size: 1rem; font-weight: 600; cursor: pointer;
            font-family: inherit; letter-spacing: 0.5px; transition: 0.2s;
            margin-top: 8px;
        }
        .btn-deploy:hover {
            background: linear-gradient(135deg, #2ea043, #3fb950);
            box-shadow: 0 6px 24px rgba(63,185,80,0.3); transform: translateY(-1px);
        }
        .btn-deploy:disabled {
            background: #21262d; color: #484f58; cursor: not-allowed;
            box-shadow: none; transform: none;
        }
        .result {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 20px; display: none;
            margin-top: 16px; text-align: center; animation: fadeIn 0.3s ease;
        }
        .result.show { display: block; }
        .result.success { border-color: rgba(63,185,80,0.4); background: rgba(63,185,80,0.05); }
        .result.error { border-color: rgba(248,81,73,0.4); background: rgba(248,81,73,0.05); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .result .url-box {
            background: var(--bg); border: 1px solid var(--border);
            border-radius: 6px; padding: 10px 14px; margin-top: 10px;
            word-break: break-all;
        }
        .result .url-box a { color: var(--accent); text-decoration: none; font-size: 0.85rem; }
        .result .url-box a:hover { text-decoration: underline; }
        .copy-btn {
            background: var(--border); border: none; color: var(--text);
            padding: 6px 12px; border-radius: 4px; cursor: pointer;
            font-size: 0.8rem; margin-top: 8px; transition: 0.2s;
        }
        .copy-btn:hover { background: var(--accent); color: #fff; }
        .rules {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 16px 20px; margin-top: 16px;
        }
        .rules h4 { font-size: 0.85rem; margin-bottom: 10px; }
        .rules ul { list-style: none; font-size: 0.8rem; color: var(--text2); }
        .rules ul li { padding: 4px 0; display: flex; align-items: flex-start; gap: 6px; }
        .rules ul li::before { content: "•"; color: var(--accent); }
        .contact {
            display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;
        }
        .contact-btn {
            flex: 1; min-width: 140px; display: flex; align-items: center;
            justify-content: center; gap: 8px; padding: 12px 16px;
            border-radius: 8px; text-decoration: none; font-size: 0.85rem;
            font-weight: 500; border: 1px solid var(--border); transition: 0.2s;
        }
        .contact-btn.wa {
            background: rgba(37,211,102,0.1); color: #25d366;
            border-color: rgba(37,211,102,0.3);
        }
        .contact-btn.wa:hover {
            background: rgba(37,211,102,0.2); box-shadow: 0 4px 16px rgba(37,211,102,0.2);
        }
        .contact-btn.tg {
            background: rgba(0,136,204,0.1); color: #0088cc;
            border-color: rgba(0,136,204,0.3);
        }
        .contact-btn.tg:hover {
            background: rgba(0,136,204,0.2); box-shadow: 0 4px 16px rgba(0,136,204,0.2);
        }
        .spinner {
            display: inline-block; width: 16px; height: 16px;
            border: 2px solid #fff; border-radius: 50%;
            border-top-color: transparent; animation: spin 0.6s linear infinite;
            margin-right: 6px; vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .footer-text {
            text-align: center; margin-top: 20px; font-size: 0.75rem; color: var(--text2);
        }
        .footer-text span { color: var(--accent); }
        @media (max-width: 480px) {
            .header h1 { font-size: 1.5rem; }
            .card { padding: 16px; }
            .contact { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-badge">🚀 DEPLOY GRATIS</div>
            <h1>XINN DEPLOY</h1>
            <p class="by">Deploy Website by <span>XINN</span></p>
        </div>

        <!-- BANNER DARI FILE LOKAL -->
        <div class="banner">
            <img src="{{ url_for('static', filename='img/banner.gif') }}" alt="XINN DEPLOY Banner" loading="lazy">
        </div>

        <div class="card">
            <div class="card-title">
                <span class="icon">📄</span> Upload File HTML
            </div>
            <form id="deployForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Nama Website</label>
                    <input type="text" name="site_name" id="siteName" placeholder="contoh: webku-by-xinn" maxlength="50" required>
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
                <button type="submit" class="btn-deploy" id="deployBtn">🚀 Deploy</button>
            </form>
        </div>

        <div class="result" id="resultBox">
            <div style="font-size:2rem;" id="resultIcon"></div>
            <h3 id="resultTitle"></h3>
            <div class="url-box" id="urlBox" style="display:none;">
                <a id="deployedUrl" href="#" target="_blank"></a>
                <br>
                <button class="copy-btn" onclick="copyUrl()">📋 Copy URL</button>
            </div>
            <p id="resultMsg" style="color:var(--text2); margin-top:8px;"></p>
        </div>

        <div class="rules">
            <h4>📌 Syarat & Ketentuan</h4>
            <ul>
                <li>File wajib bernama <strong>index.html</strong> (rename dulu sebelum upload).</li>
                <li>Tidak boleh mengandung konten ilegal, phishing, atau malware.</li>
                <li>Website bersifat <strong>publik & gratis</strong> — siapa pun bisa akses.</li>
                <li>Isi nama website, pilih file HTML, lalu klik <strong>Deploy</strong>.</li>
            </ul>
        </div>

        <div class="contact">
            <a href="https://wa.me/6283175050030?text=Halo%20XINN,%20saya%20butuh%20bantuan%20deploy." target="_blank" class="contact-btn wa">
                💬 WhatsApp – 083175050030
            </a>
            <a href="https://t.me/xinn_93" target="_blank" class="contact-btn tg">
                ✈️ Telegram – @xinn_93
            </a>
        </div>

        <p class="footer-text">Credit by <span>XINN</span> • Deploy Website Gratis © 2024</p>
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
            const urlBox = document.getElementById("urlBox");
            const deployedUrl = document.getElementById("deployedUrl");

            resultBox.className = "result";
            resultBox.style.display = "none";
            urlBox.style.display = "none";

            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Deploying...';

            const formData = new FormData(this);
            try {
                const response = await fetch("/deploy", { method: "POST", body: formData });
                const data = await response.json();
                if (data.status === "success") {
                    resultBox.classList.add("show", "success");
                    resultIcon.textContent = "✅";
                    resultTitle.textContent = "✔ Website Berhasil Dibuat!";
                    urlBox.style.display = "block";
                    deployedUrl.href = data.url;
                    deployedUrl.textContent = data.url;
                } else {
                    resultBox.classList.add("show", "error");
                    resultIcon.textContent = "❌";
                    resultTitle.textContent = "Gagal!";
                    resultMsg.textContent = data.message;
                }
            } catch (err) {
                resultBox.classList.add("show", "error");
                resultIcon.textContent = "❌";
                resultTitle.textContent = "Error!";
                resultMsg.textContent = "Gagal terhubung ke server.";
            }
            btn.disabled = false;
            btn.innerHTML = "🚀 Deploy";
        });

        function copyUrl() {
            const url = document.getElementById("deployedUrl").textContent;
            const btn = event.target;
            navigator.clipboard.writeText(url).then(() => {
                btn.textContent = "✅ Copied!";
                setTimeout(() => { btn.textContent = "📋 Copy URL"; }, 2000);
            }).catch(() => {
                const ta = document.createElement("textarea");
                ta.value = url; document.body.appendChild(ta);
                ta.select(); document.execCommand("copy");
                document.body.removeChild(ta);
                btn.textContent = "✅ Copied!";
                setTimeout(() => { btn.textContent = "📋 Copy URL"; }, 2000);
            });
        }
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
    
    safe_name = ''.join(c for c in site_name if c.isalnum() or c in '-_')
    if len(safe_name) < 3:
        return jsonify({'status': 'error', 'message': 'Nama website minimal 3 karakter!'})
    
    if 'html_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'File HTML wajib diupload!'})
    
    file = request.files['html_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'File tidak boleh kosong!'})
    
    if not file.filename.lower().endswith(('.html', '.htm')):
        return jsonify({'status': 'error', 'message': 'Format file harus .html atau .htm!'})
    
    site_folder = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
    os.makedirs(site_folder, exist_ok=True)
    file_path = os.path.join(site_folder, 'index.html')
    file.save(file_path)
    
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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], safe_name, 'index.html')
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return '''
        <!DOCTYPE html>
        <html><head><title>404</title></head>
        <body style="background:#0d1117;color:#c9d1d9;text-align:center;padding-top:100px;font-family:sans-serif;">
            <h1 style="font-size:4rem;">404</h1>
            <p>Website tidak ditemukan.</p>
            <a href="/" style="color:#58a6ff;">← Kembali ke XINN DEPLOY</a>
        </body></html>
        ''', 404

# ==================== MAIN ====================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

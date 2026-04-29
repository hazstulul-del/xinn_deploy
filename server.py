from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 3 * 1024 * 1024
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'deployed_sites')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/deploy', methods=['POST'])
def deploy():
    name = request.form.get('site_name', '').strip()
    if not name: return jsonify({'status':'error','message':'Nama wajib diisi'})
    safe = ''.join(c for c in name if c.isalnum() or c in '-_')
    if len(safe) < 3: return jsonify({'status':'error','message':'Minimal 3 karakter'})
    if 'html_file' not in request.files: return jsonify({'status':'error','message':'File wajib diupload'})
    file = request.files['html_file']
    if file.filename == '': return jsonify({'status':'error','message':'File kosong'})
    folder = os.path.join(UPLOAD_FOLDER, safe)
    os.makedirs(folder, exist_ok=True)
    file.save(os.path.join(folder, 'index.html'))
    url = f"{request.host_url.rstrip('/')}/site/{safe}"
    return jsonify({'status':'success','url':url})

@app.route('/site/<name>')
def view_site(name):
    safe = ''.join(c for c in name if c.isalnum() or c in '-_')
    folder = os.path.join(UPLOAD_FOLDER, safe)
    if os.path.exists(os.path.join(folder, 'index.html')):
        return send_from_directory(folder, 'index.html')
    return 'Website tidak ditemukan. <a href="/">Kembali</a>', 404

HTML = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XINN DEPLOY - Deploy Website Gratis</title>
    <style>
        :root { --bg: #0d1117; --card: #161b22; --border: #30363d; --accent: #58a6ff; --green: #3fb950; --text: #c9d1d9; --text2: #8b949e; }
        * { margin:0; padding:0; box-sizing:border-box; }
        body { font-family:'Segoe UI',sans-serif; background:var(--bg); color:var(--text); min-height:100vh; display:flex; justify-content:center; align-items:center; padding:20px; }
        .container { width:100%; max-width:480px; }
        .header { text-align:center; margin-bottom:20px; }
        .header-badge { display:inline-block; background:rgba(88,166,255,0.1); border:1px solid rgba(88,166,255,0.3); color:var(--accent); padding:6px 16px; border-radius:20px; font-size:0.8rem; letter-spacing:1px; margin-bottom:10px; }
        .header h1 { font-size:2rem; font-weight:700; background:linear-gradient(135deg, #58a6ff, #3fb950); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
        .header .by { color:var(--text2); font-size:0.9rem; } .header .by span { color:var(--accent); font-weight:600; }
        .banner { border-radius:12px; overflow:hidden; margin-bottom:20px; border:2px solid var(--border); }
        .banner img { width:100%; display:block; }
        .card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:24px; margin-bottom:16px; }
        .card-title { font-size:1rem; font-weight:600; margin-bottom:16px; display:flex; align-items:center; gap:8px; }
        .form-group { margin-bottom:14px; }
        .form-group label { display:block; font-size:0.85rem; color:var(--text2); margin-bottom:4px; }
        .form-group input[type="text"] { width:100%; padding:10px 14px; background:var(--bg); border:1px solid var(--border); border-radius:8px; color:var(--text); font-size:0.9rem; outline:none; }
        .form-group input[type="text"]:focus { border-color:var(--accent); }
        .file-upload { position:relative; }
        .file-upload input[type="file"] { position:absolute; width:100%; height:100%; opacity:0; cursor:pointer; z-index:2; }
        .file-upload-label { display:flex; align-items:center; gap:8px; padding:14px; background:var(--bg); border:2px dashed var(--border); border-radius:8px; cursor:pointer; justify-content:center; font-size:0.9rem; }
        .file-upload-label:hover { border-color:var(--accent); }
        .file-name { font-size:0.75rem; color:var(--text2); margin-top:4px; text-align:center; }
        .btn-deploy { width:100%; padding:14px; background:linear-gradient(135deg, #238636, #2ea043); border:none; border-radius:8px; color:#fff; font-size:1rem; font-weight:600; cursor:pointer; margin-top:6px; }
        .btn-deploy:hover { box-shadow:0 6px 24px rgba(63,185,80,0.3); }
        .btn-deploy:disabled { opacity:0.5; cursor:not-allowed; }
        .result { border-radius:8px; padding:12px; display:none; margin-top:10px; text-align:center; }
        .result.show { display:block; }
        .result.success { background:rgba(63,185,80,0.1); border:1px solid rgba(63,185,80,0.4); color:var(--green); }
        .result.error { background:rgba(248,81,73,0.1); border:1px solid rgba(248,81,73,0.4); color:#f85149; }
        .rules { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:14px 18px; margin-top:16px; }
        .rules h4 { font-size:0.85rem; margin-bottom:8px; }
        .rules ul { list-style:none; font-size:0.8rem; color:var(--text2); }
        .rules ul li { padding:3px 0; } .rules ul li::before { content:"• "; color:var(--accent); }
        .contact { display:flex; gap:12px; margin-top:16px; flex-wrap:wrap; }
        .contact-btn { flex:1; min-width:130px; display:flex; align-items:center; justify-content:center; gap:8px; padding:12px; border-radius:8px; text-decoration:none; font-size:0.85rem; border:1px solid var(--border); }
        .contact-btn.wa { background:rgba(37,211,102,0.1); color:#25d366; border-color:rgba(37,211,102,0.3); }
        .contact-btn.tg { background:rgba(0,136,204,0.1); color:#0088cc; border-color:rgba(0,136,204,0.3); }
        .footer-text { text-align:center; margin-top:20px; font-size:0.75rem; color:var(--text2); }
        .footer-text span { color:var(--accent); }
        .spinner { display:inline-block; width:14px; height:14px; border:2px solid #fff; border-radius:50%; border-top-color:transparent; animation:spin 0.6s linear infinite; margin-right:6px; vertical-align:middle; }
        @keyframes spin { to { transform:rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-badge">🚀 DEPLOY GRATIS</div>
            <h1>XINN DEPLOY</h1>
            <p class="by">Deploy Website by <span>XINN</span></p>
        </div>
        <div class="banner">
            <img src="{{ url_for('static', filename='img/banner.gif') }}" alt="Banner">
        </div>
        <div class="card">
            <div class="card-title">📄 Upload File HTML</div>
            <form id="deployForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Nama Website</label>
                    <input type="text" name="site_name" id="siteName" placeholder="contoh: webku-by-xinn" maxlength="30" required>
                </div>
                <div class="form-group">
                    <label>Upload File HTML</label>
                    <div class="file-upload">
                        <input type="file" name="html_file" id="fileInput" accept=".html,.htm" required>
                        <div class="file-upload-label">📁 <span id="uploadText">Pilih File HTML</span></div>
                    </div>
                    <div class="file-name" id="fileName">Tidak ada file yang dipilih</div>
                </div>
                <button type="submit" class="btn-deploy" id="deployBtn">🚀 Deploy Sekarang</button>
            </form>
            <div class="result" id="resultBox"></div>
        </div>
        <div class="rules">
            <h4>📌 Syarat & Ketentuan</h4>
            <ul>
                <li>File wajib bernama <strong>index.html</strong>.</li>
                <li>Tidak boleh mengandung konten ilegal.</li>
                <li>Website bersifat <strong>publik & gratis</strong>.</li>
            </ul>
        </div>
        <div class="contact">
            <a href="https://wa.me/6283175050030" target="_blank" class="contact-btn wa">💬 WhatsApp</a>
            <a href="https://t.me/xinn_93" target="_blank" class="contact-btn tg">✈️ Telegram</a>
        </div>
        <p class="footer-text">Credit by <span>XINN</span> • Deploy Website Gratis © 2026</p>
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
                    resultBox.innerHTML = '✅ <a href="' + data.url + '" target="_blank" style="color:#3fb950;">' + data.url + '</a>';
                    document.getElementById("deployForm").reset();
                    uploadText.textContent = "Pilih File HTML";
                    fileName.textContent = "Tidak ada file yang dipilih";
                } else {
                    resultBox.classList.add("show", "error");
                    resultBox.textContent = "❌ " + data.message;
                }
            } catch (err) {
                resultBox.classList.add("show", "error");
                resultBox.textContent = "❌ Gagal terhubung ke server.";
            }
            btn.disabled = false;
            btn.innerHTML = "🚀 Deploy Sekarang";
        });
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

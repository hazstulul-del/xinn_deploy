#!/usr/bin/env python3
"""
XINN DEPLOY V3 — Versi Stabil (No Crash)
Penyimpanan: GitHub API (permanen)
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import base64
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ================== KONFIGURASI ==================
# AMBIL DARI ENVIRONMENT VARIABLE (RAILWAY)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "ISI_DISINI_KALO_LOKAL")
GITHUB_USERNAME = "hazstulul-del"
REPO_NAME = "xin-deploy-sites"
# =================================================

GITHUB_API = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>XINN DEPLOY V3 - Deploy Website Gratis</title>
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
        .container { max-width: 800px; margin: 0 auto; }

        /* HEADER */
        .header { text-align: center; margin-bottom: 24px; }
        .header-badge {
            display: inline-block; background: rgba(88,166,255,0.1);
            border: 1px solid rgba(88,166,255,0.3); color: var(--accent);
            padding: 6px 16px; border-radius: 20px; font-size: 0.8rem;
            letter-spacing: 1px; margin-bottom: 10px;
        }
        .header h1 {
            font-size: 2.2rem; font-weight: 700;
            background: linear-gradient(135deg, #58a6ff, #3fb950);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .header .by { color: var(--text2); font-size: 0.9rem; }
        .header .by span { color: var(--accent); font-weight: 600; }

        /* BANNER */
        .banner {
            border-radius: 12px; overflow: hidden; margin-bottom: 24px;
            border: 2px solid var(--border); box-shadow: 0 8px 32px rgba(0,0,0,0.5);
            max-height: 250px;
        }
        .banner img { width: 100%; display: block; object-fit: cover; }

        /* GRID LAYOUT */
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
            margin-bottom: 16px;
        }
        @media (max-width: 700px) {
            .main-grid { grid-template-columns: 1fr; }
        }

        /* CARD */
        .card {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 20px;
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

        /* FORM */
        .form-group { margin-bottom: 14px; }
        .form-group label {
            display: block; font-size: 0.8rem; font-weight: 500;
            margin-bottom: 4px; color: var(--text2);
        }
        .form-group input[type="text"] {
            width: 100%; padding: 10px 14px; background: var(--bg);
            border: 1px solid var(--border); border-radius: 8px;
            color: var(--text); font-size: 0.9rem; outline: none; font-family: inherit;
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
            display: flex; align-items: center; gap: 8px;
            padding: 12px 14px; background: var(--bg);
            border: 2px dashed var(--border); border-radius: 8px;
            cursor: pointer; justify-content: center; font-size: 0.85rem; transition: 0.2s;
        }
        .file-upload-label:hover { border-color: var(--accent); }
        .file-name {
            font-size: 0.75rem; color: var(--text2);
            margin-top: 4px; text-align: center;
        }
        .btn-deploy {
            width: 100%; padding: 12px;
            background: linear-gradient(135deg, #238636, #2ea043);
            border: none; border-radius: 8px; color: #fff;
            font-size: 0.95rem; font-weight: 600; cursor: pointer;
            font-family: inherit; transition: 0.2s; margin-top: 4px;
        }
        .btn-deploy:hover {
            background: linear-gradient(135deg, #2ea043, #3fb950);
            box-shadow: 0 6px 24px rgba(63,185,80,0.3);
        }
        .btn-deploy:disabled { opacity: 0.5; cursor: not-allowed; }
        .spinner {
            display: inline-block; width: 14px; height: 14px;
            border: 2px solid #fff; border-radius: 50%;
            border-top-color: transparent; animation: spin 0.6s linear infinite;
            margin-right: 6px; vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }

        /* RESULT */
        .result {
            border-radius: 8px; padding: 12px; display: none; margin-top: 10px;
            text-align: center; font-size: 0.85rem; animation: fadeIn 0.3s ease;
        }
        .result.show { display: block; }
        .result.success { background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.4); color: var(--green); }
        .result.error { background: rgba(248,81,73,0.1); border: 1px solid rgba(248,81,73,0.4); color: var(--danger); }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

        /* RIWAYAT DEPLOY */
        .history-list { max-height: 350px; overflow-y: auto; }
        .history-item {
            display: flex; align-items: center; justify-content: space-between;
            padding: 12px 14px; border-bottom: 1px solid var(--border);
            transition: 0.2s; gap: 10px;
        }
        .history-item:last-child { border-bottom: none; }
        .history-item:hover { background: rgba(88,166,255,0.03); }
        .history-info { flex: 1; min-width: 0; }
        .history-name {
            font-weight: 600; font-size: 0.9rem; color: var(--accent);
            text-decoration: none;
        }
        .history-name:hover { text-decoration: underline; }
        .history-time {
            font-size: 0.7rem; color: var(--text2); margin-top: 2px;
        }
        .history-badge {
            background: rgba(63,185,80,0.15); color: var(--green);
            padding: 3px 10px; border-radius: 12px; font-size: 0.7rem;
            white-space: nowrap;
        }
        .empty-history {
            text-align: center; padding: 40px 20px; color: var(--text2);
        }
        .empty-history .icon-big { font-size: 3rem; margin-bottom: 12px; }
        .count-badge {
            background: var(--accent); color: #fff;
            padding: 2px 8px; border-radius: 10px; font-size: 0.7rem;
            margin-left: 6px;
        }

        /* RULES */
        .rules {
            background: var(--card); border: 1px solid var(--border);
            border-radius: 12px; padding: 14px 18px; margin-top: 16px;
        }
        .rules h4 { font-size: 0.85rem; margin-bottom: 8px; }
        .rules ul { list-style: none; font-size: 0.78rem; color: var(--text2); }
        .rules ul li { padding: 3px 0; display: flex; align-items: flex-start; gap: 6px; }
        .rules ul li::before { content: "•"; color: var(--accent); }

        /* CONTACT */
        .contact {
            display: flex; gap: 12px; margin-top: 16px; flex-wrap: wrap;
        }
        .contact-btn {
            flex: 1; min-width: 130px; display: flex; align-items: center;
            justify-content: center; gap: 8px; padding: 12px;
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

        /* FOOTER */
        .footer-text {
            text-align: center; margin-top: 20px; font-size: 0.75rem; color: var(--text2);
        }
        .footer-text span { color: var(--accent); }

        /* SCROLLBAR */
        .history-list::-webkit-scrollbar { width: 4px; }
        .history-list::-webkit-scrollbar-track { background: transparent; }
        .history-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="header-badge">🚀 DEPLOY GRATIS V3</div>
            <h1>XINN DEPLOY</h1>
            <p class="by">Deploy Website by <span>XINN</span></p>
        </div>

        <!-- BANNER -->
        <div class="banner">
            <img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExb3c4eG5mNnR5eG1hZ3QwcmZ4d2t2cXBnb3h6eTJpZ3JzOGJkYiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/26tn33aiTi1jkl6H6/giphy.gif" alt="Banner" loading="lazy">
        </div>

        <!-- MAIN GRID -->
        <div class="main-grid">
            <!-- KOLOM KIRI: FORM DEPLOY -->
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
                    <button type="submit" class="btn-deploy" id="deployBtn">🚀 Deploy Sekarang</button>
                </form>
                <div class="result" id="resultBox">
                    <div id="resultIcon"></div>
                    <span id="resultTitle"></span>
                    <div id="resultMsg" style="font-size:0.8rem; margin-top:4px;"></div>
                </div>
            </div>

            <!-- KOLOM KANAN: RIWAYAT DEPLOY -->
            <div class="card">
                <div class="card-title">
                    <span class="icon">🕐</span> Riwayat Deploy
                    <span class="count-badge" id="historyCount">0</span>
                </div>
                <div class="history-list" id="historyList">
                    <div class="empty-history">
                        <div class="icon-big">📭</div>
                        <p>Belum ada yang deploy.</p>
                        <p style="font-size:0.75rem;">Jadi yang pertama! 🚀</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- RULES -->
        <div class="rules">
            <h4>📌 Syarat & Ketentuan</h4>
            <ul>
                <li>File wajib bernama <strong>index.html</strong> (rename dulu sebelum upload).</li>
                <li>Tidak boleh mengandung konten ilegal, phishing, atau malware.</li>
                <li>Website bersifat <strong>publik & gratis</strong> — siapa pun bisa akses.</li>
                <li>Maksimal ukuran file: <strong>5 MB</strong>.</li>
            </ul>
        </div>

        <!-- CONTACT -->
        <div class="contact">
            <a href="https://wa.me/6283175050030?text=Halo%20XINN,%20saya%20butuh%20bantuan%20deploy." target="_blank" class="contact-btn wa">
                💬 WhatsApp – 083175050030
            </a>
            <a href="https://t.me/xinn_93" target="_blank" class="contact-btn tg">
                ✈️ Telegram – @xinn_93
            </a>
        </div>

        <!-- FOOTER -->
        <p class="footer-text">Credit by <span>XINN</span> • Deploy Website Gratis © 2024 • V3</p>
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

        // Load riwayat saat halaman dibuka
        loadHistory();

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
                    // Refresh riwayat
                    loadHistory();
                    // Reset form
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

        async function loadHistory() {
            try {
                const response = await fetch("/history");
                const data = await response.json();
                
                const historyList = document.getElementById("historyList");
                const historyCount = document.getElementById("historyCount");
                
                if (data.history && data.history.length > 0) {
                    historyCount.textContent = data.history.length;
                    historyList.innerHTML = data.history.map((item, index) => `
                        <div class="history-item">
                            <div class="history-info">
                                <a href="${item.url}" target="_blank" class="history-name">
                                    🌐 ${item.name}
                                </a>
                                <div class="history-time">📅 ${item.time}</div>
                            </div>
                            <span class="history-badge">#${index + 1}</span>
                        </div>
                    `).join('');
                } else {
                    historyCount.textContent = "0";
                    historyList.innerHTML = `
                        <div class="empty-history">
                            <div class="icon-big">📭</div>
                            <p>Belum ada yang deploy.</p>
                            <p style="font-size:0.75rem;">Jadi yang pertama! 🚀</p>
                        </div>
                    `;
                }
            } catch (err) {
                console.error("Gagal load history:", err);
            }
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
        return jsonify({'status': 'error', 'message': 'Nama minimal 3 karakter!'})
    
    if 'html_file' not in request.files:
        return jsonify({'status': 'error', 'message': 'File HTML wajib diupload!'})
    
    file = request.files['html_file']
    if file.filename == '':
        return jsonify({'status': 'error', 'message': 'File tidak boleh kosong!'})
    
    if not file.filename.lower().endswith(('.html', '.htm')):
        return jsonify({'status': 'error', 'message': 'Format file harus .html!'})
    
    try:
        html_content = file.read().decode('utf-8')
        
        # Upload HTML ke GitHub
        path_html = f"sites/{safe_name}/index.html"
        push_to_github(path_html, html_content, f"Deploy: {safe_name}")
        
        # Update riwayat
        history = get_history()
        history.insert(0, {
            "name": safe_name,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M WIB"),
            "url": f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/sites/{safe_name}/"
        })
        # Simpan ma

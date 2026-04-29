#!/usr/bin/env python3
"""
XINN DEPLOY V3 — Backend Saja
"""

from flask import Flask, render_template, request, jsonify
import requests
import base64
import os
import json
from datetime import datetime

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_USERNAME = "hazstulul-del"
REPO_NAME = "xin-deploy-sites"

GITHUB_API = f"https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents"
HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

@app.route('/')
def index():
    return render_template('index.html')

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
        path_html = f"sites/{safe_name}/index.html"
        push_to_github(path_html, html_content, f"Deploy: {safe_name}")
        history = get_history()
        history.insert(0, {
            "name": safe_name,
            "time": datetime.now().strftime("%d-%m-%Y %H:%M WIB"),
            "url": f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/sites/{safe_name}/"
        })
        history = history[:50]
        push_to_github("history.json", json.dumps(history, indent=2, ensure_ascii=False), f"Update history: +{safe_name}")
        public_url = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/sites/{safe_name}/"
        return jsonify({
            'status': 'success',
            'message': f'Website "{safe_name}" berhasil dideploy!',
            'url': public_url
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Server error: {str(e)}'})

@app.route('/history')
def history_route():
    history = get_history()
    return jsonify({'history': history})

def push_to_github(path, content, commit_message):
    url = f"{GITHUB_API}/{path}"
    sha = None
    check = requests.get(url, headers=HEADERS)
    if check.status_code == 200:
        sha = check.json().get("sha")
    payload = {
        "message": commit_message,
        "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
        "branch": "main"
    }
    if sha:
        payload["sha"] = sha
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code not in [200, 201]:
        raise Exception(f"GitHub API Error: {response.json().get('message', 'Unknown error')}")
    return response.json()

def get_history():
    try:
        url = f"{GITHUB_API}/history.json"
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            content = base64.b64decode(response.json()["content"]).decode('utf-8')
            return json.loads(content)
        return []
    except Exception:
        return []

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

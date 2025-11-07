# app.py (Versi Final Paling Keren dan Lengkap)

import os
import json
import threading
import time
from flask import Flask, render_template_string, request, redirect, url_for, flash, Response, jsonify
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from integrity_checker import logger, create_full_baseline, verify_integrity
from queue import Queue
import re

app = Flask(__name__)
app.secret_key = 'kunci_rahasia_paling_final_dan_keren'
LOG_FILE = "security.log"
CONFIG_FILE = "config.json"
update_queue = Queue()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Monitoring Keamanan</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <style>
        :root {
            --bg-grad-start: #eef1f5;
            --bg-grad-end: #f7f8fa;
            --card-bg: #ffffff;
            --shadow: 0 10px 25px rgba(0, 0, 0, 0.05);
            --header-color: #1c3d5a;
            --text-color: #333;
            --text-muted: #6c757d;
            --safe-color: #28a745;
            --modified-color: #ffc107;
            --deleted-color: #dc3545;
            --new-color: #17a2b8;
            --time-color: #6c757d;
        }
        body { 
            font-family: 'Poppins', sans-serif; 
            background-image: linear-gradient(120deg, var(--bg-grad-start) 0%, var(--bg-grad-end) 100%);
            margin: 0; 
            padding: 2.5em; 
            color: var(--text-color);
        }
        .container { max-width: 1400px; margin: auto; }
        header h1 { color: var(--header-color); text-align: center; margin-bottom: 2em; font-weight: 700; font-size: 2.5rem; }
        .card { 
            background-color: var(--card-bg); 
            border-radius: 16px; 
            padding: 2em; 
            box-shadow: var(--shadow); 
            margin-bottom: 2em;
            transition: all 0.3s ease-in-out;
        }
        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.08);
        }
        .grid-2-col { display: grid; grid-template-columns: 1fr 1fr; gap: 2em; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 2em; }
        .summary-card { display: flex; align-items: center; }
        .summary-card .icon { font-size: 1.8rem; width: 60px; height: 60px; border-radius: 50%; display: grid; place-items: center; color: #fff; margin-right: 1.2em; }
        .summary-card .icon.safe { background-color: var(--safe-color); }
        .summary-card .icon.modified { background-color: var(--modified-color); }
        .summary-card .icon.deleted { background-color: var(--deleted-color); }
        .summary-card .icon.new { background-color: var(--new-color); }
        .summary-card .icon.time { background-color: var(--time-color); }
        .summary-card .info h3 { margin: 0; font-size: 1rem; color: var(--text-muted); font-weight: 500; }
        .summary-card .info p { margin: 0; font-size: 2.2rem; font-weight: 700; }
        .summary-card .info p.time-text { font-size: 1.1rem; font-weight: 500; }
        .log-box { background-color: #2e2e2e; color: #e0e0e0; border-radius: 8px; padding: 1.5em; height: 450px; overflow-y: auto; white-space: pre-wrap; font-family: 'Fira Code', 'Courier New', monospace; font-size: 0.95rem; display: flex; flex-direction: column-reverse; }
        .log-line { padding-bottom: 5px; margin-top: 5px; opacity: 0.9; } .log-line.warning { color: #ff8c8c; font-weight: 600; } .log-line.info { color: #a5d6a7; }
        form label { display: block; margin-bottom: 8px; font-weight: 600; color: var(--header-color); }
        form input, form textarea, form button { width: 100%; box-sizing: border-box; padding: 12px; border-radius: 8px; border: 1px solid #ccc; margin-bottom: 15px; }
        form textarea { height: 120px; resize: vertical; }
        form button { background-color: var(--header-color); color: white; cursor: pointer; border: none; font-weight: 600; font-size: 1rem; transition: background-color 0.2s; }
        form button:hover { background-color: #2c5b8a; }
        .flash { padding: 1em; margin-bottom: 1em; border-radius: 8px; text-align: center; font-weight: 600; }
        .flash.success { background-color: #d4edda; color: #155724; } .flash.error { background-color: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <header><h1>Dashboard Monitoring Keamanan</h1></header>
        <div class="summary-grid card">
            <div class="summary-card"><div class="icon safe"><i class="fas fa-check-circle"></i></div><div class="info"><h3>File Aman</h3><p id="safe-count">{{ summary.safe }}</p></div></div>
            <div class="summary-card"><div class="icon modified"><i class="fas fa-pencil-alt"></i></div><div class="info"><h3>File Diubah (Rusak)</h3><p id="modified-count">{{ summary.modified }}</p></div></div>
            <div class="summary-card"><div class="icon deleted"><i class="fas fa-trash-alt"></i></div><div class="info"><h3>File Dihapus</h3><p id="deleted-count">{{ summary.deleted }}</p></div></div>
            <div class="summary-card"><div class="icon new"><i class="fas fa-plus-circle"></i></div><div class="info"><h3>File Baru</h3><p id="new-count">{{ summary.new }}</p></div></div>
            <div class="summary-card"><div class="icon time"><i class="fas fa-history"></i></div><div class="info"><h3>Anomali Terakhir</h3><p class="time-text" id="last-anomaly-time">{{ summary.last_anomaly_time }}</p></div></div>
        </div>
        {% with messages = get_flashed_messages(with_categories=true) %} {% if messages %}{% for category, message in messages %}<div class="flash {{ category }}">{{ message }}</div>{% endfor %}{% endif %} {% endwith %}
        <div class="grid-2-col">
            <div class="card"><h2>Buat Aset Baru</h2><form action="/create_new" method="post"><label for="new_path">Path & Nama</label><input type="text" name="new_path" placeholder="e.g., folder_baru atau secure_files/file_baru.txt" required><label for="file_content">Isi File (opsional)</label><textarea name="file_content"></textarea><button type="submit">Buat & Amankan</button></form></div>
            <div class="card"><h2>Daftarkan Aset yang Sudah Ada</h2><form action="/register_existing" method="post"><label for="existing_path">Path Folder atau File</label><input type="text" name="existing_path" placeholder="e.g., secure_files atau C:/Users/Public/dokumen.txt" required><button type="submit">Daftarkan & Amankan</button></form></div>
        </div>
        <div class="card"><h2>Detail Log (Real-time)</h2><div class="log-box" id="log-box">
            {% for line in logs %}<div class="log-line {% if 'WARNING' in line %}warning{% else %}info{% endif %}">{{ line }}</div>{% endfor %}
        </div></div>
    </div>
<script>
    const safeEl=document.getElementById('safe-count'),modifiedEl=document.getElementById('modified-count'),deletedEl=document.getElementById('deleted-count'),newEl=document.getElementById('new-count'),lastAnomalyEl=document.getElementById('last-anomaly-time'),logBox=document.getElementById('log-box');async function updateDashboard(){try{const e=await fetch('/get_latest_data'),t=await e.json();safeEl.textContent=t.summary.safe,modifiedEl.textContent=t.summary.modified,deletedEl.textContent=t.summary.deleted,newEl.textContent=t.summary.new,lastAnomalyEl.textContent=t.summary.last_anomaly_time,logBox.innerHTML="",t.logs.forEach(e=>{const t=document.createElement('div');t.className="log-line",e.includes("WARNING")?t.classList.add("warning"):t.classList.add("info"),t.textContent=e,logBox.appendChild(t)})}catch(e){console.error("Gagal:",e)}}const eventSource=new EventSource("/stream");eventSource.onmessage=function(e){"UPDATE"===e.data&&updateDashboard()};
</script>
</body>
</html>
"""

def get_current_summary_and_logs(all_logs=None):
    if all_logs is None:
        try:
            with open(LOG_FILE, 'r') as f: all_logs = f.read().strip().split('\n')
        except FileNotFoundError:
            return {"safe": 0, "modified": 0, "deleted": 0, "new": 0, "last_anomaly_time": "N/A"}, []
    
    results = verify_integrity()
    summary = {key: len(value) for key, value in results.items()}
    
    # Cari waktu anomali terakhir
    last_anomaly_time = "Tidak ada anomali"
    for log in reversed(all_logs):
        if "WARNING" in log:
            match = re.search(r'\[(.*?)\]', log)
            if match:
                last_anomaly_time = match.group(1)
                break
    summary["last_anomaly_time"] = last_anomaly_time
    
    return summary, all_logs

class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        time.sleep(1)
        if not event.is_directory:
            print(f"Perubahan terdeteksi: {event.src_path}. Memicu verifikasi...")
            logger.info("--- Memulai Pengecekan Integritas ---")
            results = verify_integrity()
            # Log hanya anomali agar tidak terlalu berisik
            for filepath in results["modified"]: logger.warning(f'DIUBAH (RUSAK): File "{filepath}"')
            for filepath in results["deleted"]: logger.warning(f'DIHAPUS: File "{filepath}"')
            for filepath in results["new"]: logger.warning(f'BARU: File "{filepath}"')
            logger.info("--- Pengecekan Selesai ---")
            update_queue.put("UPDATE")

def start_monitoring():
    try:
        with open(CONFIG_FILE, 'r') as f: config = json.load(f)
        paths_to_watch = config.get("monitored_folders", [])
    except: paths_to_watch = []
    event_handler = ChangeHandler()
    observer = Observer()
    for path in paths_to_watch:
        if os.path.isdir(path):
            observer.schedule(event_handler, path, recursive=True)
            logger.info(f"Memulai pemantauan untuk: {path}")
    observer.start()
    observer.join()

# --- Rute (Routes) tidak berubah dari versi sebelumnya ---
@app.route('/stream')
def stream():
    def event_stream():
        while True:
            signal = update_queue.get()
            yield f"data: {signal}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route('/get_latest_data')
def get_latest_data():
    summary, all_logs = get_current_summary_and_logs()
    all_logs.reverse()
    return jsonify({"summary": summary, "logs": all_logs})

@app.route('/')
def dashboard():
    summary, all_logs = get_current_summary_and_logs()
    all_logs.reverse()
    return render_template_string(HTML_TEMPLATE, logs=all_logs, summary=summary)

@app.route('/create_new', methods=['POST'])
def create_new():
    path = request.form.get('new_path').strip().replace('\\', '/')
    content = request.form.get('file_content', '')
    if not path or '..' in path:
        flash("Error: Path tidak valid.", 'error')
        return redirect(url_for('dashboard'))
    is_file = '.' in os.path.basename(path)
    try:
        if is_file:
            dir_name = os.path.dirname(path)
            if dir_name and not os.path.exists(dir_name): os.makedirs(dir_name)
            with open(path, 'w', encoding='utf-8') as f: f.write(content)
            flash(f"File '{path}' dibuat.", 'success')
            register_asset(path)
        else:
            if not os.path.exists(path): os.makedirs(path); flash(f"Folder '{path}' dibuat.", 'success')
            else: flash(f"Folder '{path}' sudah ada.", 'success')
            register_asset(path)
    except Exception as e:
        flash(f"Gagal membuat aset: {e}", 'error')
    return redirect(url_for('dashboard'))

@app.route('/register_existing', methods=['POST'])
def register_existing():
    path = request.form.get('existing_path').strip().replace('\\', '/')
    if not path or not os.path.exists(path):
        flash(f"Error: Path '{path}' tidak ada.", 'error')
        return redirect(url_for('dashboard'))
    register_asset(path)
    return redirect(url_for('dashboard'))

def register_asset(path):
    is_file = os.path.isfile(path)
    key = "monitored_files" if is_file else "monitored_folders"
    try:
        with open(CONFIG_FILE, 'r+') as f:
            config = json.load(f)
            if key not in config: config[key] = []
            if path not in config[key]:
                config[key].append(path)
                f.seek(0); json.dump(config, f, indent=4); f.truncate()
                flash(f"Aset '{path}' didaftarkan.", 'success')
            else:
                flash(f"Aset '{path}' sudah terdaftar.", 'success')
    except:
        flash("Error: Gagal update config.json.", 'error')
        return
    flash("Baseline diperbarui...", 'success')
    create_full_baseline()
    flash("PENTING: RESTART aplikasi untuk memulai pemantauan baru.", 'error')

if __name__ == '__main__':
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f: json.dump({"monitored_folders": [], "monitored_files": []}, f, indent=4)
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()
    app.run(host='0.0.0.0', port=5000, debug=False)
# app.py (Versi Desain Baru)

from flask import Flask, render_template_string
import re
import os # Direkomendasikan untuk path yang lebih aman

# --- Konstanta ---
LOG_FILE = "security.log"

app = Flask(__name__)

def get_report_data():
    """Membaca file log dan mengekstrak data untuk laporan."""
    try:
       with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        return 0, 0, "File log tidak ditemukan.", []

    safe_files_count = 0
    corrupted_files_count = 0
    last_anomaly_time = "N/A"
    
    # Gunakan set untuk memastikan kita hanya menghitung setiap file sekali per sesi monitoring terakhir
    # Kita cari sesi monitoring terakhir
    last_session_lines = []
    for i in range(len(lines) - 1, -1, -1):
        if "--- Memulai Pengecekan Integritas File ---" in lines[i]:
            last_session_lines = lines[i:]
            break
    
    # Jika tidak ada sesi, gunakan semua log (fallback)
    if not last_session_lines:
        last_session_lines = lines

    processed_files = set()
    anomalies_found = False

    for line in last_session_lines:
        # Ekstrak nama file dari log
        file_match = re.search(r'File "(.+?)"', line)
        if not file_match:
            continue
        
        filename = file_match.group(1)

        if "verified OK" in line and filename not in processed_files:
            safe_files_count += 1
            processed_files.add(filename)
        elif ("integrity failed" in line or "deleted" in line) and filename not in processed_files:
            corrupted_files_count += 1
            processed_files.add(filename)
            anomalies_found = True
        
        # Cari anomali (termasuk file baru) untuk menentukan waktu terakhir
        if "WARNING" in line or "ALERT" in line:
            time_match = re.search(r'\[(.*?)\]', line)
            if time_match:
                last_anomaly_time = time_match.group(1)
                anomalies_found = True

    if not anomalies_found:
        last_anomaly_time = "Tidak ada anomali terdeteksi"

    return safe_files_count, corrupted_files_count, last_anomaly_time, lines

@app.route('/')
def report_web():
    safe, corrupted, last_anomaly, all_logs = get_report_data()
    
    # Balik urutan log agar yang terbaru di atas
    all_logs.reverse()
    logs_content = "".join(all_logs)

    # Template HTML dengan CSS modern
    html_template = """
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Dasbor Monitoring Keamanan</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
        <style>
            :root {
                --bg-color: #f0f2f5;
                --card-bg: #ffffff;
                --text-color: #333;
                --header-color: #1c3d5a;
                --safe-color: #28a745;
                --danger-color: #dc3545;
                --shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
            }
            body {
                font-family: 'Poppins', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-color);
                margin: 0;
                padding: 2em;
            }
            .container {
                max-width: 1200px;
                margin: auto;
            }
            header {
                text-align: center;
                margin-bottom: 2.5em;
            }
            header h1 {
                color: var(--header-color);
                font-weight: 700;
                font-size: 2.5rem;
            }
            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5em;
                margin-bottom: 2.5em;
            }
            .card {
                background-color: var(--card-bg);
                border-radius: 12px;
                padding: 1.5em;
                box-shadow: var(--shadow);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                display: flex;
                align-items: center;
            }
            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
            }
            .card .icon {
                font-size: 2.5rem;
                margin-right: 0.8em;
                padding: 0.5em;
                border-radius: 50%;
                color: #fff;
            }
            .card .icon.safe { background-color: var(--safe-color); }
            .card .icon.danger { background-color: var(--danger-color); }
            .card .icon.time { background-color: #6c757d; }

            .card .info h3 {
                margin: 0;
                font-size: 1rem;
                color: #666;
                font-weight: 400;
            }
            .card .info p {
                margin: 0;
                font-size: 2rem;
                font-weight: 600;
                color: var(--text-color);
            }
            .card .info p.time-text {
                font-size: 1rem;
                font-weight: 400;
            }
            .log-container {
                background-color: var(--card-bg);
                border-radius: 12px;
                padding: 1.5em;
                box-shadow: var(--shadow);
            }
            .log-container h2 {
                margin-top: 0;
                color: var(--header-color);
            }
            .log-box {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                padding: 1em;
                height: 400px;
                overflow-y: auto;
                white-space: pre-wrap;
                font-family: 'Courier New', Courier, monospace;
                font-size: 0.9rem;
                color: #495057;
            }
            /* Custom Scrollbar */
            .log-box::-webkit-scrollbar { width: 8px; }
            .log-box::-webkit-scrollbar-track { background: #f1f1f1; }
            .log-box::-webkit-scrollbar-thumb { background: #ccc; border-radius: 4px; }
            .log-box::-webkit-scrollbar-thumb:hover { background: #aaa; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>Dasbor Monitoring Keamanan File</h1>
            </header>

            <div class="summary-grid">
                <div class="card">
                    <div class="icon safe"><i class="fas fa-check-circle"></i></div>
                    <div class="info">
                        <h3>Jumlah File Aman</h3>
                        <p>{{ safe_files }}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="icon danger"><i class="fas fa-exclamation-triangle"></i></div>
                    <div class="info">
                        <h3>Jumlah Anomali</h3>
                        <p>{{ corrupted_files }}</p>
                    </div>
                </div>
                <div class="card">
                    <div class="icon time"><i class="fas fa-clock"></i></div>
                    <div class="info">
                        <h3>Anomali Terakhir</h3>
                        <p class="time-text">{{ last_anomaly }}</p>
                    </div>
                </div>
            </div>

            <div class="log-container">
                <h2>Detail Log (Terbaru di Atas)</h2>
                <div class="log-box">{{ logs_content }}</div>
            </div>
        </div>
    </body>
    </html>
    """

    return render_template_string(html_template, 
                                  safe_files=safe, 
                                  corrupted_files=corrupted, 
                                  last_anomaly=last_anomaly,
                                  logs_content=logs_content)

if __name__ == '__main__':
    # host='0.0.0.0' agar bisa diakses dari perangkat lain di jaringan yang sama
    app.run(debug=True, host='0.0.0.0')
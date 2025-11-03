# report.py

import re

LOG_FILE = "security.log"

def generate_report():
    """Membaca file log dan menghasilkan laporan pemantauan."""
    
    try:
        with open(LOG_FILE, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"File log '{LOG_FILE}' tidak ditemukan. Jalankan 'monitor.py' terlebih dahulu.")
        return

    safe_files = 0
    corrupted_files = 0
    last_anomaly_time = None
    
    # Set untuk memastikan file yang sama tidak dihitung berulang kali per sesi
    processed_files = set()

    for line in lines:
        # Cari file yang diverifikasi OK
        if "verified OK" in line:
            # Ekstrak nama file untuk tracking unik
            match = re.search(r'File "(.+?)"', line)
            if match:
                filename = match.group(1)
                if filename not in processed_files:
                    safe_files += 1
                    processed_files.add(filename)

        # Cari file yang rusak atau anomali lainnya
        if "WARNING" in line or "ALERT" in line or "CRITICAL" in line:
            # Ambil timestamp dari log
            match = re.search(r'\[(.*?)\]', line)
            if match:
                last_anomaly_time = match.group(1)
            
            # Hitung file yang rusak (integrity failed)
            if "integrity failed" in line:
                 match_file = re.search(r'File "(.+?)"', line)
                 if match_file:
                    filename = match_file.group(1)
                    if filename not in processed_files:
                        corrupted_files += 1
                        processed_files.add(filename)


    print("--- Laporan Monitoring Keamanan ---")
    print(f"Jumlah file yang aman      : {safe_files}")
    print(f"Jumlah file rusak          : {corrupted_files}")
    
    if last_anomaly_time:
        print(f"Waktu terakhir ada anomali : {last_anomaly_time}")
    else:
        print("Waktu terakhir ada anomali : Tidak ada anomali yang tercatat.")
    print("---------------------------------")


if __name__ == "__main__":
    generate_report()
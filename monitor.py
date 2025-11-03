# monitor.py

import os
import json
import logging
from create_baseline import calculate_hash # Impor fungsi dari file sebelah

# --- Konstanta ---
FOLDER_TO_MONITOR = "secure_files"
BASELINE_FILE = "hash_db.json"
LOG_FILE = "security.log"

# --- Setup Logging ---
def setup_logging():
    """Mengkonfigurasi logger untuk menulis ke file dan konsol."""
    logger = logging.getLogger('FileIntegrityMonitor')
    logger.setLevel(logging.INFO)

    # Hapus handler yang mungkin sudah ada agar tidak ada log duplikat
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Format log sesuai permintaan
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', 
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Tambahkan handler ke logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# --- Fungsi Utama ---
def verify_integrity(logger):
    """Memverifikasi integritas file berdasarkan baseline."""
    
    # 1. Muat baseline
    try:
        with open(BASELINE_FILE, 'r') as f:
            baseline = json.load(f)
    except FileNotFoundError:
        logger.critical(f"File baseline '{BASELINE_FILE}' tidak ditemukan. Jalankan 'create_baseline.py' terlebih dahulu.")
        return
    except json.JSONDecodeError:
        logger.critical(f"Error saat membaca file baseline '{BASELINE_FILE}'. File mungkin rusak.")
        return

    # 2. Dapatkan kondisi file saat ini
    current_files = {}
    if os.path.isdir(FOLDER_TO_MONITOR):
        for filename in os.listdir(FOLDER_TO_MONITOR):
            filepath = os.path.join(FOLDER_TO_MONITOR, filename)
            if os.path.isfile(filepath):
                current_files[filepath] = calculate_hash(filepath)

    # 3. Bandingkan dan log
    baseline_files = set(baseline.keys())
    current_files_set = set(current_files.keys())

    # File yang tidak berubah (Verified OK)
    # File yang diubah (Integrity Failed)
    for filepath in baseline_files.intersection(current_files_set):
        if baseline[filepath] == current_files[filepath]:
            logger.info(f'File "{os.path.basename(filepath)}" verified OK.')
        else:
            logger.warning(f'File "{os.path.basename(filepath)}" integrity failed!')

    # File yang dihapus
    for filepath in baseline_files - current_files_set:
        logger.warning(f'File "{os.path.basename(filepath)}" has been deleted!')

    # File yang baru ditambahkan
    for filepath in current_files_set - baseline_files:
        logger.warning(f'Unknown file "{os.path.basename(filepath)}" detected.')

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("--- Memulai Pengecekan Integritas File ---")
    verify_integrity(logger)
    logger.info("--- Pengecekan Integritas File Selesai ---")
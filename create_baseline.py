# create_baseline.py

import os
import hashlib
import json

FOLDER_TO_MONITOR = "secure_files"
BASELINE_FILE = "hash_db.json"

def calculate_hash(filepath):
    """Menghitung hash SHA-256 dari sebuah file."""
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            # Baca file dalam bentuk chunk untuk efisiensi memori
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError as e:
        print(f"Error saat membaca file {filepath}: {e}")
        return None

def create_baseline():
    """Membuat dan menyimpan baseline hash dari semua file di folder target."""
    baseline = {}
    print(f"Membuat baseline untuk folder: '{FOLDER_TO_MONITOR}'...")

    if not os.path.isdir(FOLDER_TO_MONITOR):
        print(f"Error: Folder '{FOLDER_TO_MONITOR}' tidak ditemukan.")
        return

    for filename in os.listdir(FOLDER_TO_MONITOR):
        filepath = os.path.join(FOLDER_TO_MONITOR, filename)
        if os.path.isfile(filepath):
            file_hash = calculate_hash(filepath)
            if file_hash:
                baseline[filepath] = file_hash
                print(f"  - {filepath}: {file_hash}")
    
    try:
        with open(BASELINE_FILE, "w") as f:
            json.dump(baseline, f, indent=4)
        print(f"\nBaseline berhasil disimpan di '{BASELINE_FILE}'")
    except IOError as e:
        print(f"Error saat menyimpan baseline: {e}")

if __name__ == "__main__":
    create_baseline()
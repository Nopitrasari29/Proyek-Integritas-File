# integrity_checker.py (Versi Final Lengkap)

import os
import hashlib
import json
import logging

BASELINE_FILE = "hash_db.json"
LOG_FILE = "security.log"
CONFIG_FILE = "config.json"

def setup_logging():
    logger = logging.getLogger('FileIntegrator')
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        file_handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger

logger = setup_logging()

def calculate_hash(filepath):
    sha256_hash = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except IOError: return None

def get_folder_state_recursive(folder_path):
    folder_state = {}
    for dirpath, _, filenames in os.walk(folder_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            normalized_path = filepath.replace('\\', '/')
            file_hash = calculate_hash(filepath)
            if file_hash:
                folder_state[normalized_path] = file_hash
    return folder_state

def create_full_baseline():
    try:
        with open(CONFIG_FILE, 'r') as f: config = json.load(f)
        monitored_folders = config.get("monitored_folders", [])
        monitored_files = config.get("monitored_files", [])
    except (FileNotFoundError, json.JSONDecodeError):
        monitored_folders, monitored_files = [], []
    
    full_baseline = {}
    for folder in monitored_folders:
        if os.path.isdir(folder):
            full_baseline.update(get_folder_state_recursive(folder))
    for file_path in monitored_files:
        if os.path.isfile(file_path):
            normalized_path = file_path.replace('\\', '/')
            full_baseline[normalized_path] = calculate_hash(file_path)

    with open(BASELINE_FILE, "w") as f: json.dump(full_baseline, f, indent=4)
    print(f"Baseline berhasil dibuat ulang.")
    return True

def verify_integrity():
    try:
        with open(BASELINE_FILE, 'r') as f: baseline = json.load(f)
    except: baseline = {}
    try:
        with open(CONFIG_FILE, 'r') as f: config = json.load(f)
        monitored_folders = config.get("monitored_folders", [])
        monitored_files = config.get("monitored_files", [])
    except: monitored_folders, monitored_files = [], []

    current_state = {}
    for folder in monitored_folders:
        if os.path.isdir(folder):
            current_state.update(get_folder_state_recursive(folder))
    for file_path in monitored_files:
        if os.path.isfile(file_path):
            normalized_path = file_path.replace('\\', '/')
            current_state[normalized_path] = calculate_hash(file_path)

    baseline_files = set(baseline.keys())
    current_files = set(current_state.keys())
    
    safe, modified, deleted, new = [], [], [], []
    for filepath in baseline_files.intersection(current_files):
        if baseline[filepath] == current_state[filepath]: safe.append(filepath)
        else: modified.append(filepath)
    for filepath in baseline_files - current_files: deleted.append(filepath)
    for filepath in current_files - baseline_files: new.append(filepath)
        
    return {"safe": safe, "modified": modified, "deleted": deleted, "new": new}
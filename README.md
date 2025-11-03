# Proyek Sistem Deteksi Integritas File

Proyek ini adalah implementasi sistem pemantauan integritas file sederhana yang dibangun menggunakan Python. Sistem ini dirancang untuk memantau folder tertentu, mendeteksi perubahan yang tidak sah (modifikasi, penambahan, atau penghapusan file), mencatat semua aktivitas, dan menyajikan laporan melalui antarmuka web yang dinamis menggunakan Flask.

## Anggota Kelompok

| Nama Lengkap                        | NRP        |
| ----------------------------------- | ---------- |
| Aswalia Novitriasari                | 5027231012 |
| Agnes Zenobia Griselda Petrina      | 2027231034 |
| Rafika Az Zahra Kusumastuti         | 5027231050 |
| Nisrina Atiqah Dwi Putri Ridzki     | 5027231075 |

## Fitur Utama

-   **Pemantauan Folder**: Secara aktif memantau folder `./secure_files/` untuk setiap perubahan.
-   **Verifikasi Integritas**: Menggunakan hash SHA-256 untuk membuat *baseline* dan memverifikasi integritas file.
-   **Logging Komprehensif**: Semua aktivitas, baik normal (`INFO`) maupun mencurigakan (`WARNING`), dicatat ke dalam file `security.log` dengan format yang jelas (timestamp, level, pesan).
-   **Dasbor Web Dinamis**: Menyajikan laporan ringkas dan detail log melalui antarmuka web yang dibangun dengan Flask, menampilkan status keamanan sistem secara *real-time*.
-   **Simulasi Laporan**: Script tambahan untuk menampilkan ringkasan laporan langsung di terminal.

## Teknologi yang Digunakan

-   **Python**: Bahasa pemrograman utama.
-   **Flask**: Kerangka kerja web mikro untuk membangun dasbor laporan.
-   **HTML/CSS**: Untuk struktur dan gaya antarmuka web.

## Struktur Proyek

```
proyek-integritas-file/
├── secure_files/          # Folder yang dipantau
├── app.py                 # Aplikasi web Flask untuk dasbor
├── create_baseline.py     # Script untuk membuat hash awal (baseline)
├── monitor.py             # Script utama untuk memantau folder
├── report.py              # Script untuk menampilkan laporan di terminal
├── hash_db.json           # (dibuat otomatis) Database baseline hash
├── security.log           # (dibuat otomatis) File log aktivitas
└── README.md              # Dokumentasi proyek
```

## Cara Menjalankan Proyek

### 1. Persiapan Lingkungan

-   Pastikan Anda sudah menginstal Python di sistem Anda.
-   Buka terminal atau command prompt, arahkan ke folder proyek.
-   Instal dependensi yang diperlukan (Flask):
    ```bash
    pip install Flask
    ```

### 2. Alur Penggunaan

Proyek ini dijalankan melalui serangkaian skrip di terminal.

**Langkah A: Membuat Baseline Awal**
Jalankan skrip ini sekali di awal untuk mencatat kondisi "aman" dari file di dalam `secure_files`.

```bash
python create_baseline.py
```

**Langkah B: Simulasikan Perubahan**
Ubah file secara manual di dalam folder `secure_files`. Anda bisa:
-   Mengedit isi file.
-   Menghapus file.
-   Menambahkan file baru.

**Langkah C: Jalankan Monitor**
Jalankan skrip monitor untuk mendeteksi perubahan yang Anda buat. Semua temuan akan dicatat di `security.log`.

```bash
python monitor.py
```

**Langkah D: Lihat Laporan**
Anda bisa melihat laporan melalui dua cara:

1.  **Melalui Terminal**:
    ```bash
    python report.py
    ```

2.  **Melalui Dasbor Web (Direkomendasikan)**:
    ```bash
    python app.py
    ```
    Setelah server berjalan, buka browser dan akses alamat `http://127.0.0.1:5000`.

## Tampilan Dasbor

Berikut adalah tampilan dasbor saat mendeteksi anomali dan saat sistem dalam kondisi aman.

**Kondisi Waspada (Anomali Terdeteksi)**

<img width="465" height="441" alt="Screenshot 2025-11-03 080103" src="https://github.com/user-attachments/assets/56b3a5f2-8895-4208-a343-6eadda83a88b" />


**Kondisi Aman (Semua File Terverifikasi)**

<img width="466" height="398" alt="Screenshot 2025-11-03 075849" src="https://github.com/user-attachments/assets/8d93cdda-82a3-49db-9d17-a93fe89f8085" />

---

# Dashboard Monitoring Keamanan File

Selamat datang di Proyek Sistem Deteksi Integritas File! Ini adalah sebuah aplikasi keamanan berbasis web yang dirancang untuk memantau file dan folder penting secara *real-time*. Sistem ini secara otomatis mendeteksi perubahan yang tidak sah, mencatat setiap aktivitas, dan menyajikan laporan visual melalui dashboard interaktif yang modern.

Dibangun dengan Python dan Flask, proyek ini melampaui pemantauan dasar dengan menyediakan fitur dinamis untuk membuat dan mendaftarkan aset digital baru yang perlu dilindungi langsung dari antarmuka web.

## Tim Pengembang

| Nama Lengkap                        | NRP        |
| ----------------------------------- | ---------- |
| Aswalia Novitriasari                | 5027231012 |
| Agnes Zenobia Griselda Petrina      | 2027231034 |
| Rafika Az Zahra Kusumastuti         | 5027231050 |
| Nisrina Atiqah Dwi Putri Ridzki     | 5027231075 |

---

## Fitur Unggulan

-   **Dashboard Real-time**: Memantau status keamanan file tanpa perlu me-refresh halaman. Setiap anomali akan langsung memperbarui tampilan.
-   **Monitoring Otomatis**: Menggunakan `watchdog` untuk mendeteksi perubahan file secara instan di latar belakang.
-   **Dukungan Aset Fleksibel**: Mampu memantau folder beserta seluruh isinya (termasuk sub-folder) dan file tunggal secara spesifik.
-   **Klasifikasi Anomali Detail**: Membedakan dengan jelas antara file yang **diubah (rusak)**, file yang **dihapus**, dan file **baru** yang tidak dikenal.
-   **Manajemen Aset via Web**:
    -   **Buat Aset Baru**: Membuat folder atau file baru langsung dari dashboard.
    -   **Daftarkan Aset yang Ada**: Menambahkan folder atau file yang sudah ada ke dalam daftar pantauan.
-   **Logging Komprehensif**: Semua aktivitas tercatat secara permanen di `security.log` untuk keperluan audit dan analisis.

## Teknologi yang Digunakan

-   **Python**: Bahasa pemrograman utama.
-   **Flask**: Kerangka kerja web untuk membangun dashboard dan API.
-   **Watchdog**: Library Python untuk memantau perubahan file sistem secara efisien.
-   **Server-Sent Events (SSE)**: Teknologi untuk mendorong pembaruan data dari server ke browser secara *real-time*.
-   **HTML, CSS, JavaScript**: Untuk membangun antarmuka pengguna yang interaktif dan responsif.

---

## Alur Kerja Sistem (Flow)

Sistem ini memiliki alur kerja yang cerdas dan terintegrasi antara proses latar belakang (monitor) dan antarmuka pengguna (web).

1.  **Inisialisasi**:
    -   Saat `app.py` dijalankan, ia akan memulai dua *thread* utama:
        1.  **Web Server (Flask)**: Menangani permintaan HTTP dan menyajikan dashboard.
        2.  **File Monitor (Watchdog)**: Membaca `config.json` dan mulai mengawasi semua folder yang terdaftar di latar belakang.

2.  **Deteksi Perubahan (Real-time)**:
    -   Ketika pengguna mengubah, menghapus, atau membuat file di dalam folder yang dipantau, **Watchdog** akan langsung mendeteksi *event* tersebut.
    -   Watchdog memicu fungsi `verify_integrity()` dari `integrity_checker.py`.

3.  **Verifikasi & Logging**:
    -   Fungsi `verify_integrity()` membandingkan *state* file saat ini dengan *baseline* di `hash_db.json`.
    -   Hasilnya (file mana yang aman, diubah, dihapus, atau baru) dikembalikan.
    -   Aplikasi kemudian mencatat semua anomali yang ditemukan ke dalam file `security.log` sebagai `WARNING`.

4.  **Pembaruan ke Dashboard (Real-time Push)**:
    -   Setelah selesai mencatat, aplikasi mengirimkan sinyal **"UPDATE"** sederhana ke *stream* SSE.
    -   JavaScript di browser, yang selalu terhubung ke *stream* ini, menerima sinyal "UPDATE".
    -   Setelah menerima sinyal, JavaScript segera membuat permintaan `fetch` ke endpoint `/get_latest_data` di server.
    -   Server merespons dengan data JSON terbaru yang berisi ringkasan (jumlah file aman, rusak, dll.) dan daftar log lengkap.
    -   JavaScript kemudian memperbarui angka di kartu ringkasan dan me-render ulang kotak log dengan data terbaru, semua **tanpa me-refresh halaman**.

5.  **Interaksi Pengguna (Manajemen Aset)**:
    -   Pengguna menggunakan form di web untuk membuat atau mendaftarkan aset baru.
    -   Aplikasi Flask menerima permintaan ini, memodifikasi file sistem (`config.json`, membuat folder/file baru), dan memanggil `create_full_baseline()` untuk memperbarui `hash_db.json`.
    -   Pengguna kemudian diinstruksikan untuk me-restart aplikasi agar **File Monitor (Watchdog)** dapat memuat konfigurasi baru dan mulai memantau aset yang baru ditambahkan.

---

## Panduan Penggunaan

### 1. Persiapan

-   Pastikan Anda sudah menginstal Python.
-   Buka terminal di folder proyek dan instal semua dependensi:
    ```bash
    pip install Flask watchdog
    ```

### 2. Menjalankan Aplikasi

Aplikasi ini sangat mudah dijalankan.

```bash
python app.py
```
Perintah ini akan secara otomatis:
1.  Membuat `config.json` jika belum ada.
2.  Memulai server web di `http://127.0.0.1:5000`.
3.  Mengaktifkan monitor file otomatis di latar belakang.

### 3. Langkah Awal: Mendaftarkan Aset Pertama

Saat pertama kali menjalankan, belum ada yang dipantau.
1.  Buka browser Anda ke `http://127.0.0.1:5000`.
2.  Gunakan form **"Daftarkan Aset yang Sudah Ada"** untuk mendaftarkan folder pertama Anda (misalnya, `secure_files`).
3.  Ikuti instruksi di layar untuk **me-restart aplikasi** (`Ctrl+C` di terminal, lalu jalankan `python app.py` lagi).

Setelah restart, sistem Anda sudah aktif sepenuhnya dan siap digunakan!

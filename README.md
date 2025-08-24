# Proyek Glycine: Sistem Monitoring Pertanian Kedelai

  Selamat datang di dokumentasi resmi Proyek Glycine. Glycine adalah sebuah sistem monitoring pertanian presisi berbasis IoT dan WebSocket yang dirancang untuk memantau kondisi lahan secara real-time melalui dashboard web yang modern dan interaktif.

## 📋 Daftar Isi

1.  [Fitur Utama](https://www.google.com/search?q=%23-1-fitur-utama)
2.  [Tumpukan Teknologi (Tech Stack)](https://www.google.com/search?q=%23-2-tumpukan-teknologi-tech-stack)
3.  [Setup & Instalasi (Untuk Development)](https://www.google.com/search?q=%23-3-setup--instalasi-untuk-development)
4.  [Menjalankan Proyek](https://www.google.com/search?q=%23-4-menjalankan-proyek)
5.  [Panduan Implementasi untuk Perangkat IoT (Raspberry Pi)](https://www.google.com/search?q=%23-5-panduan-implementasi-untuk-perangkat-iot-raspberry-pi)

-----

## ✨ 1. Fitur Utama

  - **Dashboard Real-time**: Menampilkan data sensor secara langsung dari perangkat di lapangan tanpa perlu me-refresh halaman, lengkap dengan animasi transisi data.
  - **Manajemen Perangkat**: Antarmuka untuk menambah, mengedit, dan menghapus perangkat IoT melalui modal interaktif.
  - **Arsitektur WebSocket**: Komunikasi dua arah yang efisien antara server dan perangkat IoT menggunakan Django Channels.
  - **UI Modern & Responsif**: Tampilan yang bersih, minimalis, dan dapat diakses dari desktop (dengan sidebar *collapsible*) maupun mobile (dengan *bottom navigation*).
  - **Simulasi & Testing**: Dilengkapi dengan skrip untuk simulasi pengiriman data dari perangkat (`iot_device_simulator.py`) dan pengisian data sampel ke database (`setup_sample_data.py`).

-----

## 🛠️ 2. Tumpukan Teknologi (Tech Stack)

| Kategori | Teknologi |
| :--- | :--- |
| **Backend** | Django 5.2.5, Django Channels |
| **Server ASGI** | Daphne |
| **Database** | MySQL |
| **Frontend** | Tailwind CSS, Flowbite, JavaScript |
| **Komunikasi IoT**| WebSocket |
| **Environment** | python-decouple (`.env` file) |

-----

## 🚀 3. Setup & Instalasi (Untuk Development)

Ikuti langkah-langkah ini untuk menjalankan proyek di komputer lokal Anda.

#### **Prasyarat**

  - Python 3.10+
  - Git
  - Database MySQL yang sedang berjalan

#### **Langkah-langkah Setup**

1.  **Clone Repositori**

    ```bash
    git clone https://onesearch.id/Repositories/Repository
    cd glycine
    ```

2.  **Buat dan Aktifkan Virtual Environment**

    ```bash
    python -m venv venv
    # Untuk Windows
    venv\Scripts\activate
    # Untuk macOS / Linux
    source venv/bin/activate
    ```

3.  **Instal Dependensi**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Konfigurasi Environment (`.env`)**

      - Salin file `.env.example` menjadi `.env`.
      - Isi semua nilai yang dibutuhkan, terutama `SECRET_KEY` dan detail koneksi database (`DB_NAME`, `DB_USER`, `DB_PASSWORD`).
      - Untuk membuat `SECRET_KEY` baru secara otomatis, jalankan:
        ```bash
        python manage.py createsecretkey
        ```

5.  **Jalankan Migrasi Database**
    Perintah ini akan membuat tabel `Device` dan `SensorReading` di database Anda.

    ```bash
    python manage.py migrate
    ```

6.  **(Opsional) Isi Database dengan Data Sampel**
    Untuk langsung melihat tampilan dashboard dengan data, jalankan skrip ini:

    ```bash
    python setup_sample_data.py
    ```

-----

## ▶️ 4. Menjalankan Proyek

1.  **Jalankan Server Development**

    ```bash
    python manage.py runserver
    ```

    Aplikasi sekarang bisa diakses di `http://127.0.0.1:8000/`, yang akan otomatis mengarah ke halaman dashboard.

2.  **Akses Halaman Lain**

      - **Dashboard**: `http://127.0.0.1:8000/dashboard`
      - **Manajemen Perangkat**: `http://127.0.0.1:8000/devices`
      - **Pompa Air**: `http://127.0.0.1:8000/pompa-air`

-----

## 📡 5. Panduan Implementasi untuk Perangkat IoT (Raspberry Pi)


### **Tujuan Komunikasi**

Perangkat Anda harus terhubung ke server Glycine melalui **WebSocket** untuk mengirim data sensor dan menjaga status *online*.

### **A. Koneksi WebSocket**

  - **URL Endpoint**: Perangkat harus terhubung ke URL berikut:

    ```
    ws://<alamat_server>/ws/device/<device_uuid>/
    ```

      - **`<alamat_server>`**: Ganti dengan alamat IP dan port server Django (misal: `192.168.1.10:8000` saat development).
      - **`<device_uuid>`**: Ganti dengan UUID/MAC Address unik dari perangkat yang sudah terdaftar di sistem.

  - **Proses Koneksi**:

    1.  Saat terhubung, server akan otomatis mengubah status perangkat menjadi `online`.
    2.  Server akan mengirim pesan konfirmasi: `{"type": "connection_established", ...}`.
    3.  Saat koneksi terputus, server akan otomatis mengubah status perangkat menjadi `offline`.

### **B. Format Pengiriman Data Sensor**

Perangkat harus mengirim data dalam format **JSON** dengan struktur sebagai berikut:

```json
{
  "type": "sensor_data",
  "data": {
    "air_temperature": 29.5,
    "air_humidity": 76.0,
    "soil_moisture": 68.0,
    "soil_ph": 6.8,
    "wind_speed": 12.5,
    "wind_direction": "Tenggara",
    "nitrogen": 120.0,
    "phosphorus": 85.0,
    "potassium": 210.0,
    "rainfall": 0.5,
    "battery_level": 92
  }
}
```

  - **`type`**: Wajib diisi `"sensor_data"`.
  - **`data`**: Objek yang berisi semua nilai sensor. Jika ada sensor yang datanya tidak tersedia, kirim `null` atau jangan sertakan *key*-nya sama sekali.

### **C. Heartbeat**

Untuk menjaga koneksi tetap aktif, perangkat disarankan mengirim pesan *heartbeat* setiap 1-5 menit.

```json
{
  "type": "heartbeat",
  "timestamp": "2025-08-21T15:00:00.123Z"
}
```

### **D. Kode Referensi (Simulator)**

Cara termudah untuk memahami implementasinya adalah dengan melihat script **`iot_device_simulator.py`**. Script ini adalah contoh kerja lengkap untuk:

  - Menghubungkan ke server WebSocket.
  - Memformat pesan JSON dengan benar.
  - Mengirim data sensor dan heartbeat.
  - Menerima balasan dari server.

**Bisa mengadaptasi logika dari script ini ke dalam program utama di Raspberry Pi.** Untuk menguji, jalankan:

```bash
# Ganti UUID dengan UUID yang terdaftar
python iot_device_simulator.py AA:BB:CC:DD:EE:FF --single
```
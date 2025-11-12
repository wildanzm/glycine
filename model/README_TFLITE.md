# Soybean Disease Detection Model (TensorFlow Lite Version)

## 📘 Deskripsi Proyek

Model menerima **gambar daun kedelai** sebagai input, mengklasifikasikannya ke dalam kategori penyakit tertentu, dan memberikan **rekomendasi penanganan otomatis** berdasarkan hasil prediksi.  
Aplikasi web berbasis **Django** dapat menggunakan model ini untuk memberikan hasil diagnosis secara real-time.

---

## 🧠 Arsitektur Sistem

```
Input Gambar (Daun Kedelai)
        │
        ▼
 Preprocessing (Resize, Normalisasi)
        │
        ▼
  TensorFlow Lite Model (.tflite)
        │
        ▼
 Prediksi Label Penyakit
        │
        ▼
 Ambil Rekomendasi dari rekomendasi.json
        │
        ▼
 Hasil Akhir (Nama Penyakit + Deskripsi + Saran Penanganan)
```

---

## 🧩 File dan Struktur

| File                           | Deskripsi                                                                                                                   |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------------- |
| `soybean_disease_model.tflite` | Model CNN hasil konversi dari Keras `.h5` ke format TensorFlow Lite. Digunakan untuk inference di server atau aplikasi web. |
| `rekomendasi.json`             | File JSON berisi detail tiap penyakit: nama ilmiah, deskripsi gejala, dan rekomendasi penanganan.                           |

---

## ⚙️ Cara Menggunakan Model di Django (Server Inference)

### 1. Instalasi Library

Tambahkan dependensi berikut di `requirements.txt`:

```bash
tensorflow==2.15.0
numpy
pillow
```

> Jika ingin lebih ringan (tanpa TensorFlow penuh), bisa gunakan:
>
> ```bash
> pip install tflite-runtime
> ```
>
> Pastikan versi `tflite-runtime` sesuai dengan Python dan OS server.

---

### 2. Load dan Gunakan Model `.tflite`

Contoh implementasi di `views.py`:

```python
import json
import numpy as np
from PIL import Image
import tensorflow as tf
from django.http import JsonResponse

# Load model TFLite
interpreter = tf.lite.Interpreter(model_path="path/to/soybean_disease_model.tflite")
interpreter.allocate_tensors()

# Ambil detail input/output
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load rekomendasi
with open("path/to/rekomendasi.json", "r", encoding="utf-8") as f:
    rekomendasi_data = json.load(f)

labels = list(rekomendasi_data.keys())  # kelas sesuai urutan training

def predict_soybean(request):
    if request.method == "POST":
        img_file = request.FILES["image"]
        img = Image.open(img_file).resize((224, 224))
        img = np.array(img).astype(np.float32) / 255.0
        img = np.expand_dims(img, axis=0)

        # Set input tensor
        interpreter.set_tensor(input_details[0]['index'], img)

        # Jalankan inferensi
        interpreter.invoke()

        # Ambil hasil prediksi
        prediction = interpreter.get_tensor(output_details[0]['index'])[0]
        predicted_class = labels[np.argmax(prediction)]

        hasil = rekomendasi_data[predicted_class]

        return JsonResponse({
            "penyakit": predicted_class,
            "nama_ilmiah": hasil["nama_ilmiah"],
            "deskripsi": hasil["deskripsi"],
            "rekomendasi": hasil["rekomendasi"]
        })
```

---

## 🧾 Daftar Kelas yang Didukung

Model mendeteksi 8 kondisi utama daun kedelai:

1. **Sehat**
2. **Hawar Daun Bakteri** (_Pseudomonas savastanoi pv. glycinea_)
3. **Bercak Daun Cercospora** (_Cercospora sojina_)
4. **Embun Bulu** (_Peronospora manshurica_)
5. **Bercak Mata Kodok**
6. **Bercak Target** (_Corynespora cassiicola_)
7. **Karat Kedelai** (_Phakopsora pachyrhizi_)
8. **Kekurangan Kalium** (_Defisiensi Nutrisi (K)_)

---

## 🧪 Contoh Output API

**Request (POST)**  
`/api/predict`  
Form-data: `image: daun_kedelai.jpg`

**Response (JSON)**

```json
{
  "penyakit": "Karat Kedelai",
  "nama_ilmiah": "Phakopsora pachyrhizi",
  "deskripsi": "Penyakit jamur yang sangat merusak...",
  "rekomendasi": [
    "Segera lakukan aplikasi fungisida...",
    "Tanam varietas yang memiliki ketahanan...",
    "Pantau laporan cuaca dan peringatan dini..."
  ]
}
```

---

## 📊 Evaluasi Model

Model berbasis **MobileNetV2** dilatih pada dataset daun kedelai dengan augmentasi citra untuk meningkatkan generalisasi.  
Hasil evaluasi menunjukkan **akurasi di atas 90%** pada data validasi.

---

## 💡 Catatan Penting Integrasi

- Format model sekarang: **TensorFlow Lite (`.tflite`)**
- Input model: gambar RGB ukuran **224×224** piksel, normalisasi ke [0, 1]
- Output model: vektor probabilitas berukuran **(8,)**
- File `rekomendasi.json` wajib tersedia di path yang sama dengan model
- Jika runtime menggunakan `tflite-runtime`, maka **TensorFlow penuh tidak diperlukan**

---

## 📄 Lisensi

Proyek ini dibuat untuk tujuan penelitian dan edukasi dalam pengembangan sistem deteksi penyakit tanaman berbasis AI.

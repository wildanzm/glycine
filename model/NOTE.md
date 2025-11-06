# 🌱 Soybean Disease Detection Model

## 📘 Deskripsi Proyek

Proyek ini bertujuan untuk **mendeteksi penyakit pada daun kedelai** menggunakan **model deep learning berbasis CNN (Convolutional Neural Network)**. Model menerima **gambar daun kedelai** sebagai input, mengklasifikasikannya ke dalam kategori penyakit tertentu, dan memberikan **rekomendasi penanganan otomatis** berdasarkan hasil prediksi.

Model ini dapat diintegrasikan ke dalam aplikasi web berbasis **Django**, di mana pengguna dapat mengunggah foto daun kedelai dan menerima hasil diagnosis beserta rekomendasi.

---

## 🧠 Arsitektur Sistem

```
Input Gambar (Daun Kedelai)
        │
        ▼
 Preprocessing (Resize, Normalisasi)
        │
        ▼
   CNN Model (ResNet / Custom CNN)
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

| File                                      | Deskripsi                                                                                                                                    |
| ----------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `soybean-weight.ipynb`                    | Notebook untuk pelatihan dan penyimpanan model CNN. Berisi tahapan preprocessing, augmentasi data, arsitektur model, training, dan evaluasi. |
| `soybean_disease_model_final_weighted.h5` | Model hasil training (format Keras HDF5) yang siap di-load untuk prediksi.                                                                   |
| `rekomendasi.json`                        | File JSON berisi detail tiap penyakit: nama ilmiah, deskripsi gejala, dan rekomendasi pengendalian.                                          |

---

## ⚙️ Cara Menggunakan Model di Django

### 1. Instalasi Library

Tambahkan dependensi berikut:

```bash
tensorflow==2.10.0 / lebih
numpy
pillow
```

### 2. Load Model

Contoh integrasi di `views.py`:

```python
import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from django.http import JsonResponse

# Load model dan file rekomendasi
model = load_model("path/to/soybean_disease_model_final_weighted.h5")

with open("path/to/rekomendasi.json", "r", encoding="utf-8") as f:
    rekomendasi_data = json.load(f)

labels = list(rekomendasi_data.keys())  # kelas sesuai urutan training

def predict_soybean(request):
    if request.method == "POST":
        img_file = request.FILES["image"]
        img = image.load_img(img_file, target_size=(224, 224))
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
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

Model mendeteksi 7 kondisi utama daun kedelai:

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

Model diuji menggunakan dataset citra daun kedelai dengan beberapa kelas penyakit. Hasil evaluasi menunjukkan akurasi yang baik (>90%) dalam mendeteksi penyakit dari gambar uji dengan augmentasi data yang memadai.

---

## 💡 Catatan Integrasi

- Pastikan ukuran input gambar sesuai dengan dimensi yang digunakan saat training (misal `224x224`).
- Model harus dijalankan dalam environment yang memiliki TensorFlow.
- File `rekomendasi.json` wajib berada pada path yang sama dengan file model agar hasil prediksi dapat langsung dikaitkan dengan rekomendasi.

---

## 📄 Lisensi

Proyek ini dibuat untuk keperluan penelitian dan edukasi dalam pengembangan sistem deteksi penyakit tanaman berbasis AI.

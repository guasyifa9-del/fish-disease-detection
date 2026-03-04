# Fish Disease Detection

Sistem Deteksi Penyakit Ikan Air Tawar menggunakan Convolutional Neural Network (CNN).

## Fitur
- Upload foto ikan untuk deteksi penyakit otomatis
- 7 kelas klasifikasi (6 penyakit + sehat)
- Rekomendasi penanganan dan pencegahan
- Riwayat prediksi

## Tech Stack
- Python 3.10, Flask 2.x, TensorFlow/Keras
- Bootstrap 5, SQLite

## Setup
```bash
# 1. Jalankan setup script
setup_project.bat

# 2. Install dependencies
pip install -r requirements.txt

# 3. Jalankan aplikasi
python run.py
```

## Struktur Proyek
```
fish-disease-detection/
├── app/                    # Flask application package
│   ├── ml/                 # Machine learning module
│   ├── static/             # CSS, JS, images, uploads
│   └── templates/          # HTML templates (Jinja2)
├── models/                 # Trained CNN model (.h5)
├── notebooks/              # Jupyter notebooks
├── data/                   # Dataset (raw, processed, splits)
├── database/               # SQLite database
├── config.py               # Flask configuration
├── run.py                  # Entry point
└── requirements.txt        # Python dependencies
```

# Panduan Deployment — FishDetect
## Sistem Deteksi Penyakit Ikan Air Tawar

---

## Daftar Isi
1. [Persiapan](#1-persiapan)
2. [Deploy ke Railway (Utama)](#2-deploy-ke-railway)
3. [Deploy ke PythonAnywhere (Backup)](#3-deploy-ke-pythonanywhere-backup)
4. [Environment Variables](#4-environment-variables)
5. [Pertimbangan Performa Production](#5-pertimbangan-performa-production)
6. [Backup & Restore Database](#6-backup--restore-database)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Persiapan

### File deployment yang sudah dibuat:

| File | Fungsi |
|------|--------|
| `Procfile` | Perintah start server (gunicorn) |
| `runtime.txt` | Versi Python (3.11.9) |
| `requirements.txt` | Semua dependencies + gunicorn |
| `.env.example` | Template environment variables |
| `config.py` | ProductionConfig dengan security settings |
| `run.py` | Support PORT dari environment variable |

### Push ke GitHub terlebih dahulu:

```bash
cd fish-disease-detection

# Buat .gitignore jika belum ada
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
echo "database/*.db" >> .gitignore
echo "app/static/uploads/*" >> .gitignore
echo "!app/static/uploads/.gitkeep" >> .gitignore
echo "models/*.h5" >> .gitignore

# Init, add, commit, push
git init
git add .
git commit -m "Initial commit: FishDetect v1.0"
git branch -M main
git remote add origin https://github.com/USERNAME/fish-disease-detection.git
git push -u origin main
```

> **PENTING:** File `best_model.h5` (~165MB) melebihi limit GitHub (100MB).
> Gunakan **Git LFS** untuk upload model:
> ```bash
> git lfs install
> git lfs track "*.h5"
> git add .gitattributes models/best_model.h5
> git commit -m "Add model with LFS"
> git push
> ```

---

## 2. Deploy ke Railway

### Langkah 1: Buat Akun Railway
1. Buka [railway.app](https://railway.app)
2. Klik **"Login"** → pilih **"Login with GitHub"**
3. Authorize Railway untuk akses GitHub Anda

### Langkah 2: Buat Project Baru
1. Klik **"New Project"** di dashboard
2. Pilih **"Deploy from GitHub repo"**
3. Pilih repository **fish-disease-detection**
4. Railway akan otomatis mendeteksi Python project

### Langkah 3: Set Environment Variables
Di Settings → Variables, tambahkan:

| Variable | Value |
|----------|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | *(string acak panjang, mis: `sk-fish2024-abcdef123456`)* |
| `PORT` | *(diisi otomatis oleh Railway)* |

### Langkah 4: Deploy
1. Railway akan otomatis build dan deploy
2. Tunggu build selesai (bisa 5-10 menit karena TensorFlow besar)
3. Klik **"Generate Domain"** di Settings → Networking
4. Anda akan mendapat URL seperti: `https://fish-disease-detection-production.up.railway.app`

### Langkah 5: Verifikasi
```
Buka di browser:
https://your-app.up.railway.app/health    → cek status
https://your-app.up.railway.app/          → landing page
https://your-app.up.railway.app/upload    → coba upload
```

> **Catatan Railway:**
> - Free tier: 500 jam/bulan, 512 MB RAM
> - Model TF bisa berat — monitor RAM di dashboard
> - Jika melebihi limit, pertimbangkan upgrade ($5/bulan)

---

## 3. Deploy ke PythonAnywhere (Backup)

Jika Railway tidak berhasil (RAM tidak cukup untuk TensorFlow), gunakan PythonAnywhere.

### Langkah 1: Buat Akun
1. Buka [pythonanywhere.com](https://www.pythonanywhere.com)
2. Klik **"Start running Python online"** → pilih **Free** plan
3. Buat akun baru

### Langkah 2: Upload Project
1. Buka tab **"Consoles"** → klik **"Bash"**
2. Clone repository:
   ```bash
   git clone https://github.com/USERNAME/fish-disease-detection.git
   cd fish-disease-detection
   ```
3. Buat virtual environment:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 fishenv
   pip install -r requirements.txt
   ```

### Langkah 3: Upload Model
Karena Git LFS mungkin tidak tersedia:
1. Buka tab **"Files"**
2. Navigate ke `/home/USERNAME/fish-disease-detection/models/`
3. Upload `best_model.h5` secara manual (klik "Upload a file")

### Langkah 4: Setup Web App
1. Buka tab **"Web"** → klik **"Add a new web app"**
2. Pilih **Manual configuration** → Python 3.10
3. Set konfigurasi:
   - **Source code:** `/home/USERNAME/fish-disease-detection`
   - **Working directory:** `/home/USERNAME/fish-disease-detection`
   - **Virtualenv:** `/home/USERNAME/.virtualenvs/fishenv`

4. Edit **WSGI configuration file**, ganti isinya:
   ```python
   import sys
   import os

   # Path ke project
   project_home = '/home/USERNAME/fish-disease-detection'
   if project_home not in sys.path:
       sys.path.insert(0, project_home)

   # Set environment variables
   os.environ['FLASK_ENV'] = 'production'
   os.environ['SECRET_KEY'] = 'ganti-dengan-string-acak'

   # Import Flask app
   from run import app as application
   ```

### Langkah 5: Reload & Verifikasi
1. Klik **"Reload"** di tab Web
2. Buka: `https://USERNAME.pythonanywhere.com`

> **Catatan PythonAnywhere:**
> - Free: 1 web app, 512 MB storage, CPU limit
> - TensorFlow mungkin lambat di free tier
> - File upload terbatas di free tier
> - Kelebihan: sangat stabil, tidak perlu credit card

---

## 4. Environment Variables

| Variable | Deskripsi | Default | Required |
|----------|-----------|---------|----------|
| `FLASK_ENV` | Mode aplikasi | `development` | Ya (set `production`) |
| `SECRET_KEY` | Kunci enkripsi session | *(hardcoded)* | Ya |
| `PORT` | Port server | `5000` | Railway auto-set |
| `DATABASE_URL` | URI database | SQLite local | Tidak |

---

## 5. Pertimbangan Performa Production

### 5.1 Model Loading
- Model di-load **sekali saat startup** (sudah diimplementasi di `__init__.py`)
- Gunicorn Procfile menggunakan `--workers 1` karena TF butuh banyak RAM
- Timeout diset `120 detik` untuk memberi waktu model loading

### 5.2 Cleanup File Upload
Untuk menghemat storage di cloud, tambahkan cleanup otomatis.
Di `routes.py`, setelah prediksi berhasil, bisa tambahkan:
```python
# Opsional: hapus file setelah X hari
import time
upload_folder = app.config['UPLOAD_FOLDER']
for f in os.listdir(upload_folder):
    filepath = os.path.join(upload_folder, f)
    if os.path.getmtime(filepath) < time.time() - 7*86400:  # 7 hari
        os.remove(filepath)
```

### 5.3 Batasi Upload
- Production config sudah diset `MAX_CONTENT_LENGTH = 3 MB`
- Validasi MIME type sudah ada di routes

### 5.4 Tips Menghemat RAM
- Gunakan `tensorflow-cpu` (bukan full tensorflow) jika tidak butuh GPU:
  ```
  pip install tensorflow-cpu==2.13.1
  ```
  Ini menghemat ~200MB RAM

---

## 6. Backup & Restore Database

### Backup (Download dari server)

**Railway:**
```bash
# Tidak bisa langsung — gunakan endpoint backup
# Tambahkan route ini di routes.py (hanya untuk admin):

@main_bp.route('/admin/backup-db')
def backup_db():
    import shutil
    db_path = os.path.join(current_app.root_path, '..', 'database', 'fish_disease.db')
    return send_file(db_path, as_attachment=True, download_name='backup_fish_disease.db')
```

**PythonAnywhere:**
1. Buka tab **Files**
2. Navigate ke `fish-disease-detection/database/`
3. Klik `fish_disease.db` → **Download**

### Restore (Upload ke server)

**Local restore:**
```bash
# Simpan backup
copy database\fish_disease.db database\fish_disease_backup_20260304.db

# Restore dari backup
copy database\backup_file.db database\fish_disease.db
```

### Backup Otomatis (Script)
Jalankan secara berkala untuk backup:
```python
# backup_db.py
import shutil
from datetime import datetime

src = 'database/fish_disease.db'
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
dst = f'database/backups/fish_disease_{timestamp}.db'

shutil.copy2(src, dst)
print(f"Backup berhasil: {dst}")
```

---

## 7. Troubleshooting

### Error: "Killed" saat build (Railway)
**Penyebab:** RAM tidak cukup untuk install TensorFlow  
**Solusi:** Gunakan `tensorflow-cpu` di requirements.txt, atau upgrade Railway plan

### Error: "ModuleNotFoundError: tensorflow"
**Penyebab:** TF gagal install  
**Solusi:** Cek Python version di runtime.txt sesuai dengan TF requirements

### Error: "OSError: model file not found"
**Penyebab:** File .h5 tidak ter-upload (terlalu besar untuk GitHub)  
**Solusi:** Upload manual via Git LFS, atau upload langsung ke PythonAnywhere Files

### Error: "Address already in use"
**Penyebab:** Port sudah dipakai proses lain  
**Solusi:** Pastikan tidak ada instance Flask lain yang berjalan

### App sangat lambat di cloud
**Penyebab:** Free tier CPU/RAM terbatas  
**Solusi:**
1. Gunakan `tensorflow-cpu`
2. Kompres model (quantization)
3. Upgrade ke paid tier ($5/bulan)

---

> **Rekomendasi:** Untuk UAT pembudidaya, coba deploy ke **PythonAnywhere** terlebih dahulu karena lebih stabil di free tier dan tidak memerlukan credit card. Jika performa cukup, gunakan untuk UAT. Jika butuh performa lebih baik, upgrade ke Railway paid tier.

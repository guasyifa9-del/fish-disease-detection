"""
debug_helper.py — Pre-flight Component Checker
Fish Disease Detection System

Script untuk memeriksa apakah semua komponen siap sebelum menjalankan app:
  ✓ Python version
  ✓ Library dependencies
  ✓ Model file (.h5)
  ✓ Database file
  ✓ Upload folder
  ✓ Template files
  ✓ Static files (CSS/JS)

Jalankan: python debug_helper.py
"""

import os
import sys

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Warna terminal (ANSI)
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
BOLD = '\033[1m'
RESET = '\033[0m'

# Counter
_pass = 0
_fail = 0
_warn = 0


def ok(msg):
    global _pass
    _pass += 1
    print(f"  {GREEN}✓{RESET} {msg}")


def fail(msg):
    global _fail
    _fail += 1
    print(f"  {RED}✗{RESET} {msg}")


def warn(msg):
    global _warn
    _warn += 1
    print(f"  {YELLOW}⚠{RESET} {msg}")


def header(title):
    print(f"\n{BOLD}{CYAN}{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}{RESET}")


# ============================================================
# 1. Python Version
# ============================================================
def check_python():
    header("1. Python Version")
    v = sys.version_info
    version_str = f"{v.major}.{v.minor}.{v.micro}"
    if v.major == 3 and v.minor >= 8:
        ok(f"Python {version_str}")
    elif v.major == 3:
        warn(f"Python {version_str} (disarankan >= 3.8)")
    else:
        fail(f"Python {version_str} (butuh Python 3.8+)")


# ============================================================
# 2. Dependencies
# ============================================================
def check_dependencies():
    header("2. Library Dependencies")

    libs = {
        'flask': 'Flask',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'PIL': 'Pillow',
        'numpy': 'NumPy',
        'werkzeug': 'Werkzeug',
    }

    for module, name in libs.items():
        try:
            mod = __import__(module)
            version = getattr(mod, '__version__', '?')
            ok(f"{name} ({version})")
        except ImportError:
            fail(f"{name} — TIDAK TERINSTALL → pip install {name.lower()}")

    # TensorFlow (special case, bisa lambat)
    try:
        import tensorflow as tf
        ok(f"TensorFlow ({tf.__version__})")
    except ImportError:
        fail("TensorFlow — TIDAK TERINSTALL → pip install tensorflow")

    # pytest (opsional)
    try:
        import pytest
        ok(f"pytest ({pytest.__version__}) [opsional, untuk testing]")
    except ImportError:
        warn("pytest tidak terinstall → pip install pytest")


# ============================================================
# 3. Model File (.h5)
# ============================================================
def check_model():
    header("3. Model CNN (best_model.h5)")

    model_path = os.path.join(BASE_DIR, 'models', 'best_model.h5')

    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        ok(f"File ditemukan: {model_path}")
        ok(f"Ukuran: {size_mb:.1f} MB")

        if size_mb < 1:
            warn("Ukuran model terlalu kecil, mungkin corrupt")

        # Coba load
        try:
            import tensorflow as tf
            model = tf.keras.models.load_model(model_path)
            ok(f"Model berhasil di-load")
            ok(f"Input shape: {model.input_shape}")
            ok(f"Output shape: {model.output_shape}")

            # Verifikasi 7 output classes
            output_classes = model.output_shape[-1]
            if output_classes == 7:
                ok(f"Output classes: {output_classes} (sesuai)")
            else:
                warn(f"Output classes: {output_classes} (expected 7)")

        except ImportError:
            warn("TensorFlow tidak tersedia, skip load test")
        except Exception as e:
            fail(f"Gagal load model: {e}")
    else:
        fail(f"File TIDAK DITEMUKAN: {model_path}")
        print(f"    → Pastikan best_model.h5 ada di folder models/")


# ============================================================
# 4. Database
# ============================================================
def check_database():
    header("4. Database SQLite")

    db_dir = os.path.join(BASE_DIR, 'database')
    db_path = os.path.join(db_dir, 'fish_disease.db')

    if os.path.exists(db_dir):
        ok(f"Folder database: {db_dir}")
    else:
        warn(f"Folder database belum ada (akan dibuat otomatis)")

    if os.path.exists(db_path):
        size_kb = os.path.getsize(db_path) / 1024
        ok(f"File database: {db_path} ({size_kb:.1f} KB)")

        # Cek tabel
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()

            expected_tables = ['detections', 'diseases']
            for t in expected_tables:
                if t in tables:
                    ok(f"Tabel '{t}' ada")
                else:
                    fail(f"Tabel '{t}' TIDAK ADA")

            # Cek data penyakit
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM diseases")
            count = cursor.fetchone()[0]
            conn.close()

            if count >= 7:
                ok(f"Data penyakit: {count} record")
            else:
                warn(f"Data penyakit hanya {count} record (expected >= 7)")

        except Exception as e:
            fail(f"Error membaca database: {e}")
    else:
        warn("File database belum ada (akan dibuat saat app start)")


# ============================================================
# 5. Upload Folder
# ============================================================
def check_uploads():
    header("5. Folder Uploads")

    upload_dir = os.path.join(BASE_DIR, 'app', 'static', 'uploads')

    if os.path.exists(upload_dir):
        ok(f"Folder: {upload_dir}")
        files = os.listdir(upload_dir)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        ok(f"Jumlah gambar: {len(image_files)}")

        # Cek writable
        if os.access(upload_dir, os.W_OK):
            ok("Folder writable ✓")
        else:
            fail("Folder TIDAK writable")
    else:
        warn("Folder uploads belum ada (akan dibuat otomatis)")


# ============================================================
# 6. Template Files
# ============================================================
def check_templates():
    header("6. Template Files (Jinja2)")

    templates_dir = os.path.join(BASE_DIR, 'app', 'templates')
    required_templates = [
        'base.html',
        'index.html',
        'upload.html',
        'result.html',
        'history.html',
        'disease_info.html',
    ]

    for tpl in required_templates:
        path = os.path.join(templates_dir, tpl)
        if os.path.exists(path):
            ok(f"{tpl}")
        else:
            fail(f"{tpl} — TIDAK DITEMUKAN")


# ============================================================
# 7. Static Files (CSS/JS)
# ============================================================
def check_static():
    header("7. Static Files (CSS/JS)")

    required_files = [
        os.path.join('app', 'static', 'css', 'style.css'),
        os.path.join('app', 'static', 'js', 'main.js'),
        os.path.join('app', 'static', 'js', 'upload.js'),
    ]

    for f in required_files:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            ok(f"{f}")
        else:
            fail(f"{f} — TIDAK DITEMUKAN")


# ============================================================
# 8. App Module Structure
# ============================================================
def check_app_modules():
    header("8. App Module Structure")

    required_modules = [
        os.path.join('app', '__init__.py'),
        os.path.join('app', 'routes.py'),
        os.path.join('app', 'models.py'),
        os.path.join('app', 'utils.py'),
        os.path.join('app', 'ml', '__init__.py'),
        os.path.join('app', 'ml', 'preprocessing.py'),
        os.path.join('app', 'ml', 'model_loader.py'),
        os.path.join('app', 'ml', 'inference.py'),
        'config.py',
        'run.py',
    ]

    for f in required_modules:
        path = os.path.join(BASE_DIR, f)
        if os.path.exists(path):
            ok(f"{f}")
        else:
            fail(f"{f} — TIDAK DITEMUKAN")


# ============================================================
# MAIN
# ============================================================
def main():
    print(f"\n{BOLD}{CYAN}==================================================")
    print(f"   FishDetect -- Pre-flight Component Check")
    print(f"=================================================={RESET}")

    check_python()
    check_dependencies()
    check_model()
    check_database()
    check_uploads()
    check_templates()
    check_static()
    check_app_modules()

    # Summary
    print(f"\n{BOLD}{'='*50}")
    print(f"  RINGKASAN")
    print(f"{'='*50}{RESET}")
    print(f"  {GREEN}✓ Passed : {_pass}{RESET}")
    print(f"  {YELLOW}⚠ Warning: {_warn}{RESET}")
    print(f"  {RED}✗ Failed : {_fail}{RESET}")

    if _fail == 0:
        print(f"\n  {GREEN}{BOLD}🎉 Semua komponen siap! Jalankan: python run.py{RESET}\n")
    else:
        print(f"\n  {RED}{BOLD}❌ Perbaiki {_fail} error di atas sebelum menjalankan app.{RESET}\n")

    return 0 if _fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())

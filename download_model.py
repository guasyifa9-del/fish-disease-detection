"""
download_model.py — Download model CNN dari Google Drive
Menggunakan gdown untuk handle file besar (>100MB).

File ID Google Drive: 1b84Sc_c9uvMNL3JXOaWo-38zu5FnntMc
"""

import os
import sys

# Google Drive file ID
GDRIVE_FILE_ID = "1b84Sc_c9uvMNL3JXOaWo-38zu5FnntMc"
GDRIVE_URL = f"https://drive.google.com/uc?id={GDRIVE_FILE_ID}"
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_model.h5")


def is_valid_h5_file(filepath):
    """Cek apakah file adalah HDF5 yang valid (bukan LFS pointer)."""
    if not os.path.exists(filepath):
        return False
    if os.path.getsize(filepath) < 1_000_000:
        return False
    with open(filepath, 'rb') as f:
        header = f.read(4)
    return header == b'\x89HDF'


def ensure_model():
    """Pastikan model ada dan valid. Download jika perlu."""
    if is_valid_h5_file(MODEL_PATH):
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"[download_model] Model sudah ada: {MODEL_PATH} ({size_mb:.1f} MB)")
        return True

    print(f"[download_model] Model tidak ditemukan atau invalid.")
    print(f"[download_model] Mengunduh dari Google Drive...")

    os.makedirs(MODEL_DIR, exist_ok=True)

    try:
        import gdown
        print(f"[download_model] URL: {GDRIVE_URL}")
        print(f"[download_model] Target: {MODEL_PATH}")
        gdown.download(GDRIVE_URL, MODEL_PATH, quiet=False)

        if is_valid_h5_file(MODEL_PATH):
            size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
            print(f"[download_model] Berhasil! Model valid ({size_mb:.1f} MB)")
            return True
        else:
            print(f"[download_model] ERROR: File yang diunduh bukan HDF5 valid!")
            return False

    except Exception as e:
        print(f"[download_model] ERROR: {e}")
        return False


if __name__ == "__main__":
    success = ensure_model()
    sys.exit(0 if success else 1)

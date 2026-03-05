"""
download_model.py — Download model CNN dari Google Drive
Digunakan saat deploy ke cloud (Railway/PythonAnywhere)
di mana Git LFS tidak tersedia.

File ID Google Drive: 1b84Sc_c9uvMNL3JXOaWo-38zu5FnntMc
"""

import os
import sys
import requests

# Google Drive file ID
GDRIVE_FILE_ID = "1b84Sc_c9uvMNL3JXOaWo-38zu5FnntMc"
MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
MODEL_PATH = os.path.join(MODEL_DIR, "best_model.h5")


def is_valid_h5_file(filepath):
    """Cek apakah file adalah HDF5 yang valid (bukan LFS pointer)."""
    if not os.path.exists(filepath):
        return False
    # File terlalu kecil = kemungkinan LFS pointer
    if os.path.getsize(filepath) < 1_000_000:  # < 1MB
        return False
    # Cek magic bytes HDF5: \x89HDF
    with open(filepath, 'rb') as f:
        header = f.read(4)
    return header == b'\x89HDF'


def download_from_gdrive(file_id, destination):
    """Download file besar dari Google Drive (handle virus scan warning)."""
    print(f"[download_model] Downloading model dari Google Drive...")
    print(f"[download_model] File ID: {file_id}")
    print(f"[download_model] Target : {destination}")

    url = "https://drive.google.com/uc?export=download&confirm=1"
    session = requests.Session()

    response = session.get(url, params={"id": file_id}, stream=True)
    response.raise_for_status()

    # Simpan file
    os.makedirs(os.path.dirname(destination), exist_ok=True)
    total = 0
    with open(destination, "wb") as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
                total += len(chunk)
                mb = total / (1024 * 1024)
                if total % (10 * 1024 * 1024) < 32768:  # Print setiap ~10MB
                    print(f"[download_model] Downloaded: {mb:.1f} MB")

    final_mb = total / (1024 * 1024)
    print(f"[download_model] Selesai! Total: {final_mb:.1f} MB")
    return total


def ensure_model():
    """Pastikan model ada dan valid. Download jika perlu."""
    if is_valid_h5_file(MODEL_PATH):
        size_mb = os.path.getsize(MODEL_PATH) / (1024 * 1024)
        print(f"[download_model] Model sudah ada: {MODEL_PATH} ({size_mb:.1f} MB)")
        return True

    print(f"[download_model] Model tidak ditemukan atau invalid di: {MODEL_PATH}")
    print(f"[download_model] Mengunduh dari Google Drive...")

    try:
        total = download_from_gdrive(GDRIVE_FILE_ID, MODEL_PATH)
        if is_valid_h5_file(MODEL_PATH):
            print(f"[download_model] Model berhasil diunduh dan valid!")
            return True
        else:
            print(f"[download_model] ERROR: File yang diunduh bukan HDF5 valid!")
            return False
    except Exception as e:
        print(f"[download_model] ERROR: Gagal mengunduh model: {e}")
        return False


if __name__ == "__main__":
    success = ensure_model()
    sys.exit(0 if success else 1)

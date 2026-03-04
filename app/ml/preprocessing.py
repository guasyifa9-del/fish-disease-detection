"""
Preprocessing gambar untuk input ke model CNN.
Fish Disease Detection System.

Module ini menangani seluruh pipeline preprocessing gambar:
- Validasi format gambar
- Resize ke ukuran input model (224×224)
- Normalisasi pixel values
- Expand dimensions untuk batch prediction
"""

import os
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def preprocess_image(image_path):
    """
    Memuat dan memproses gambar agar siap diinput ke model CNN.

    Pipeline:
        1. Buka gambar menggunakan PIL/Pillow
        2. Validasi file gambar
        3. Konversi ke RGB (handle RGBA, grayscale, dll)
        4. Resize ke 224×224 piksel menggunakan LANCZOS
        5. Konversi ke array numpy float32
        6. Normalisasi pixel ke range [0, 1] (bagi 255)
        7. Expand dimensions untuk batch (shape: 1, 224, 224, 3)

    Args:
        image_path (str): Path absolut ke file gambar.
            Format yang didukung: PNG, JPG, JPEG, BMP, WEBP

    Returns:
        numpy.ndarray: Array dengan shape (1, 224, 224, 3),
            dtype float32, range [0.0, 1.0], siap untuk model.predict()

    Raises:
        FileNotFoundError: Jika file gambar tidak ditemukan
        ValueError: Jika file bukan gambar valid
        IOError: Jika gagal membaca file gambar
    """
    # Validasi file ada
    if not os.path.exists(image_path):
        logger.error(f"File gambar tidak ditemukan: {image_path}")
        raise FileNotFoundError(f"File gambar tidak ditemukan: {image_path}")

    try:
        # 1. Buka gambar menggunakan PIL
        logger.info(f"Membuka gambar: {os.path.basename(image_path)}")
        img = Image.open(image_path)

        # 2. Konversi ke RGB jika bukan RGB (handle RGBA, L, P, dll)
        if img.mode != 'RGB':
            logger.info(f"Konversi mode {img.mode} → RGB")
            img = img.convert('RGB')

        # 3. Resize ke 224×224 piksel
        original_size = img.size
        img = img.resize((224, 224), Image.LANCZOS)
        logger.debug(f"Resize: {original_size} → (224, 224)")

        # 4. Konversi ke array numpy
        img_array = np.array(img, dtype=np.float32)

        # 5. Normalisasi pixel ke range [0, 1]
        img_array = img_array / 255.0

        # 6. Expand dimensions untuk batch: (H, W, C) → (1, H, W, C)
        img_array = np.expand_dims(img_array, axis=0)

        logger.info(
            f"Preprocessing selesai — shape: {img_array.shape}, "
            f"range: [{img_array.min():.2f}, {img_array.max():.2f}]"
        )

        return img_array

    except (IOError, SyntaxError) as e:
        logger.error(f"Gagal membuka gambar: {e}")
        raise ValueError(f"File bukan gambar valid: {e}")
    except Exception as e:
        logger.error(f"Error saat preprocessing: {e}")
        raise


def validate_image(image_path):
    """
    Memvalidasi apakah file gambar valid dan bisa dibaca oleh model.

    Args:
        image_path (str): Path ke file gambar

    Returns:
        tuple: (is_valid: bool, message: str)
            - (True, 'Gambar valid.') jika file valid
            - (False, 'Pesan error') jika file tidak valid
    """
    try:
        if not os.path.exists(image_path):
            return False, f'File tidak ditemukan: {image_path}'

        img = Image.open(image_path)
        img.verify()  # Verifikasi integritas file

        # Buka ulang setelah verify (verify menutup file)
        img = Image.open(image_path)
        width, height = img.size

        if width < 10 or height < 10:
            return False, f'Gambar terlalu kecil: {width}×{height}'

        logger.info(f"Validasi OK: {os.path.basename(image_path)} ({width}×{height})")
        return True, 'Gambar valid.'

    except (IOError, SyntaxError) as e:
        return False, f'File gambar tidak valid: {str(e)}'

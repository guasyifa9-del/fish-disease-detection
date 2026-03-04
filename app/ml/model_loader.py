"""
Model Loader — Memuat model CNN untuk inferensi.
Fish Disease Detection System.

Module ini menangani loading model CNN dengan pattern singleton:
- Model di-load SEKALI saat aplikasi start (di app/__init__.py)
- Akses ke model via get_model() — tidak perlu load ulang
- Handle exception jika file .h5 tidak ditemukan
- Logging waktu loading untuk monitoring
"""

import os
import time
import logging

logger = logging.getLogger(__name__)

# Singleton: model disimpan di app/__init__.py sebagai global
# Module ini hanya menyediakan akses ke model tersebut


def load_model_once(model_path):
    """
    Memuat model CNN dari file .h5 menggunakan TensorFlow/Keras.

    Fungsi ini menggunakan pattern singleton melalui app/__init__.py:
    - Dipanggil SEKALI saat startup di _load_cnn_model()
    - Model disimpan sebagai variabel global _cnn_model
    - Request berikutnya mengakses model via get_model()

    Args:
        model_path (str): Path absolut ke file model .h5
            Contoh: 'C:/xampp/htdocs/fish-disease-detection/models/best_model.h5'

    Returns:
        tensorflow.keras.Model: Model CNN yang sudah dimuat dan siap prediksi

    Raises:
        FileNotFoundError: Jika file .h5 tidak ditemukan di path
        ImportError: Jika TensorFlow belum terinstall
        Exception: Jika terjadi error saat memuat model (format corrupt, dll)
    """
    # Validasi file model ada
    if not os.path.exists(model_path):
        logger.error(f"File model TIDAK DITEMUKAN: {model_path}")
        raise FileNotFoundError(
            f"File model tidak ditemukan: {model_path}. "
            f"Pastikan file '{os.path.basename(model_path)}' "
            f"sudah ada di folder models/. "
            f"Latih model menggunakan notebook 02_model_training.ipynb."
        )

    # Load model
    try:
        logger.info(f"Memuat model CNN dari: {model_path}")
        logger.info(f"Ukuran file: {os.path.getsize(model_path) / 1024 / 1024:.1f} MB")

        start_time = time.time()

        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)

        elapsed = time.time() - start_time

        logger.info("=" * 60)
        logger.info("  MODEL CNN BERHASIL DIMUAT!")
        logger.info(f"  File         : {os.path.basename(model_path)}")
        logger.info(f"  Input shape  : {model.input_shape}")
        logger.info(f"  Output shape : {model.output_shape}")
        logger.info(f"  Total params : {model.count_params():,}")
        logger.info(f"  Loading time : {elapsed:.2f} detik")
        logger.info("=" * 60)

        return model

    except ImportError:
        logger.error(
            "TensorFlow belum terinstall. "
            "Jalankan: pip install tensorflow"
        )
        raise

    except Exception as e:
        logger.error(f"Gagal memuat model CNN: {e}")
        raise


def get_model():
    """
    Mendapatkan instance model CNN yang sudah dimuat saat startup.

    Model di-load sekali di app/__init__.py saat pertama kali start.
    Fungsi ini mengambil model yang tersimpan di sana (singleton).

    Returns:
        tensorflow.keras.Model: Model CNN yang siap digunakan untuk prediksi

    Raises:
        RuntimeError: Jika model tidak tersedia (belum dilatih/file tidak ada)
    """
    from app import get_cnn_model, is_model_available

    if not is_model_available():
        raise RuntimeError(
            "Model CNN belum tersedia. "
            "Pastikan file 'best_model.h5' sudah ada di folder models/. "
            "Latih model menggunakan notebook 02_model_training.ipynb."
        )

    model = get_cnn_model()
    if model is None:
        raise RuntimeError("Model CNN gagal dimuat saat startup.")

    return model


def is_model_loaded():
    """
    Mengecek apakah model CNN sudah dimuat dan siap digunakan.

    Returns:
        bool: True jika model sudah dimuat dan siap prediksi,
              False jika model belum tersedia
    """
    from app import is_model_available
    return is_model_available()


def get_model_info():
    """
    Mendapatkan informasi detail tentang model yang sedang dimuat.

    Returns:
        dict: Informasi model, berisi:
            - 'loaded' (bool): Status model
            - 'input_shape' (tuple): Shape input model
            - 'output_shape' (tuple): Shape output model
            - 'total_params' (int): Total parameter model
        Atau dict dengan 'loaded': False jika model belum dimuat
    """
    if not is_model_loaded():
        return {'loaded': False, 'message': 'Model belum dimuat.'}

    from app import get_cnn_model
    model = get_cnn_model()

    return {
        'loaded': True,
        'input_shape': model.input_shape,
        'output_shape': model.output_shape,
        'total_params': model.count_params()
    }

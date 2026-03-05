"""
Flask Application Factory
Fish Disease Detection System

Module ini menginisialisasi aplikasi Flask menggunakan pola App Factory:
- Konfigurasi dari config.py
- SQLAlchemy untuk database SQLite
- Load model CNN saat startup (bukan per-request)
- Blueprint untuk modular routing
- Error handler untuk 404 dan 500
"""

import os
import logging
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# ============================================================
# Konfigurasi Logging
# ============================================================
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================
# Inisialisasi Ekstensi (di luar factory agar bisa diakses
# dari modul lain, misalnya app.models dan app.routes)
# ============================================================
db = SQLAlchemy()

# Variabel global untuk menyimpan status model
_cnn_model = None
_model_available = False


def get_cnn_model():
    """
    Getter untuk mendapatkan instance model CNN yang sudah dimuat.
    Dipanggil dari modul lain (misalnya inference.py).

    Returns:
        tensorflow.keras.Model atau None jika model tidak tersedia
    """
    return _cnn_model


def is_model_available():
    """
    Mengecek apakah model CNN berhasil dimuat dan siap digunakan.

    Returns:
        bool: True jika model tersedia, False jika tidak
    """
    return _model_available


def _load_cnn_model(app):
    """
    Memuat model CNN (.h5) saat aplikasi pertama kali start.
    Jika file model belum ada (belum selesai training),
    aplikasi tetap berjalan untuk development frontend.

    Args:
        app (Flask): Instance aplikasi Flask
    """
    global _cnn_model, _model_available

    model_path = app.config.get('MODEL_PATH')
    model_name = app.config.get('MODEL_NAME', 'best_model.h5')

    if not model_path:
        logger.warning(
            "MODEL_PATH tidak dikonfigurasi di config.py. "
            "Fitur prediksi tidak akan berfungsi."
        )
        return

    # --- Cek apakah file model ada dan valid ---
    # Jika file tidak ada atau terlalu kecil (LFS pointer),
    # coba download dari Google Drive
    need_download = False
    if not os.path.exists(model_path):
        need_download = True
    elif os.path.getsize(model_path) < 1_000_000:  # < 1MB = LFS pointer
        logger.warning("File model terlalu kecil, kemungkinan LFS pointer. Mencoba download...")
        need_download = True

    if need_download:
        try:
            from download_model import ensure_model
            if not ensure_model():
                logger.warning("Gagal download model. Fitur prediksi tidak tersedia.")
                _model_available = False
                return
        except Exception as e:
            logger.warning(f"Auto-download model gagal: {e}")
            _model_available = False
            return

    if not os.path.exists(model_path):
        logger.warning("=" * 60)
        logger.warning("  MODEL CNN TIDAK DITEMUKAN!")
        logger.warning(f"  Path: {model_path}")
        logger.warning(f"  File '{model_name}' belum ada di folder models/.")
        logger.warning("")
        logger.warning("  Aplikasi tetap berjalan dalam MODE DEVELOPMENT.")
        logger.warning("  Fitur upload & prediksi akan menampilkan pesan error.")
        logger.warning("  Silakan latih model dan simpan ke folder models/.")
        logger.warning("=" * 60)
        _model_available = False
        return

    # --- Load model menggunakan TensorFlow/Keras ---
    try:
        logger.info(f"Memuat model CNN dari: {model_path}")
        import tensorflow as tf

        # Suppress TensorFlow warnings yang tidak perlu
        tf.get_logger().setLevel('ERROR')
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

        _cnn_model = tf.keras.models.load_model(model_path)
        _model_available = True

        logger.info("=" * 60)
        logger.info("  MODEL CNN BERHASIL DIMUAT!")
        logger.info(f"  File  : {model_name}")
        logger.info(f"  Input : {_cnn_model.input_shape}")
        logger.info(f"  Output: {_cnn_model.output_shape}")
        logger.info("=" * 60)

    except ImportError:
        logger.error(
            "TensorFlow belum terinstall. "
            "Jalankan: pip install tensorflow==2.13.1"
        )
        _model_available = False

    except Exception as e:
        logger.error(f"Gagal memuat model CNN: {e}")
        logger.error(
            "Aplikasi tetap berjalan, tetapi fitur prediksi "
            "tidak akan berfungsi."
        )
        _model_available = False


def _ensure_directories(app):
    """
    Memastikan semua direktori yang dibutuhkan ada.
    Membuat folder jika belum ada.

    Args:
        app (Flask): Instance aplikasi Flask
    """
    # Folder uploads
    upload_folder = app.config.get('UPLOAD_FOLDER')
    if upload_folder:
        os.makedirs(upload_folder, exist_ok=True)
        logger.info(f"Upload folder: {upload_folder}")

    # Folder database
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if db_uri.startswith('sqlite:///'):
        db_path = db_uri.replace('sqlite:///', '')
        db_folder = os.path.dirname(db_path)
        if db_folder:
            os.makedirs(db_folder, exist_ok=True)
            logger.info(f"Database folder: {db_folder}")

    # Folder models
    model_path = app.config.get('MODEL_PATH', '')
    if model_path:
        model_folder = os.path.dirname(model_path)
        if model_folder:
            os.makedirs(model_folder, exist_ok=True)


def _register_error_handlers(app):
    """
    Mendaftarkan custom error handler untuk halaman error
    yang lebih user-friendly.

    Args:
        app (Flask): Instance aplikasi Flask
    """

    @app.errorhandler(404)
    def page_not_found(error):
        """Handler untuk error 404 - Halaman Tidak Ditemukan."""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(error):
        """Handler untuk error 500 - Internal Server Error."""
        # Rollback database session jika ada error
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(413)
    def request_entity_too_large(error):
        """Handler untuk error 413 - File terlalu besar."""
        return render_template(
            'errors/413.html'
        ), 413


def _register_context_processors(app):
    """
    Mendaftarkan context processor untuk variabel yang selalu
    tersedia di semua template.

    Args:
        app (Flask): Instance aplikasi Flask
    """

    @app.context_processor
    def inject_global_vars():
        """Menyediakan variabel global untuk semua template."""
        return {
            'app_name': 'Fish Disease Detection',
            'model_available': _model_available
        }


def create_app(config_name='development'):
    """
    Membuat dan mengkonfigurasi instance Flask (App Factory Pattern).

    Urutan inisialisasi:
        1. Buat instance Flask
        2. Load konfigurasi dari config.py
        3. Pastikan direktori yang dibutuhkan ada
        4. Inisialisasi SQLAlchemy
        5. Register Blueprint (routes)
        6. Register error handlers
        7. Register context processors
        8. Buat tabel database + seed data awal
        9. Load model CNN (sekali saat startup)

    Args:
        config_name (str): Nama konfigurasi
            - 'development' (default) → debug mode ON
            - 'production' → debug mode OFF
            - 'testing' → gunakan SQLite in-memory

    Returns:
        Flask: Instance aplikasi Flask yang sudah fully configured
    """
    app = Flask(__name__)

    # -------------------------------------------------------
    # 1. Load konfigurasi
    # -------------------------------------------------------
    from config import config_by_name
    selected_config = config_by_name.get(config_name, config_by_name['default'])
    app.config.from_object(selected_config)

    logger.info(f"Flask app dibuat dengan konfigurasi: {config_name}")

    # -------------------------------------------------------
    # 2. Pastikan semua direktori ada
    # -------------------------------------------------------
    _ensure_directories(app)

    # -------------------------------------------------------
    # 3. Inisialisasi ekstensi SQLAlchemy
    # -------------------------------------------------------
    db.init_app(app)

    # -------------------------------------------------------
    # 4. Register Blueprint (routes)
    # -------------------------------------------------------
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    # -------------------------------------------------------
    # 5. Register error handlers (404, 500, 413)
    # -------------------------------------------------------
    _register_error_handlers(app)

    # -------------------------------------------------------
    # 6. Register context processors
    # -------------------------------------------------------
    _register_context_processors(app)

    # -------------------------------------------------------
    # 7. Buat tabel database + seed data awal
    #    Menggunakan init_db() dari app.utils
    # -------------------------------------------------------
    from app.utils import init_db
    init_db(app)

    # -------------------------------------------------------
    # 8. Load model CNN sekali saat startup
    # -------------------------------------------------------
    _load_cnn_model(app)

    logger.info("=" * 60)
    logger.info("  Fish Disease Detection — App Ready!")
    logger.info(f"  Config : {config_name}")
    logger.info(f"  Model  : {'Tersedia ✓' if _model_available else 'Tidak tersedia ✗'}")
    logger.info("=" * 60)

    return app


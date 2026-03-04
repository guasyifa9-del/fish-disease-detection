"""
Konfigurasi aplikasi Flask - Fish Disease Detection
"""

import os

# Base directory proyek
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Konfigurasi dasar aplikasi."""

    # --- Flask ---
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fish-disease-secret-key-2024-change-in-production'
    DEBUG = False
    TESTING = False

    # --- Upload ---
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}

    # --- Database (SQLite) ---
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'database', 'fish_disease.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # --- Model CNN ---
    MODEL_NAME = 'best_model.h5'
    MODEL_PATH = os.path.join(BASE_DIR, 'models', MODEL_NAME)
    IMG_SIZE = (224, 224)  # Ukuran input model CNN (width, height)

    # --- Kelas Penyakit ---
    DISEASE_CLASSES = [
        'bacterial_red_disease',
        'aeromonas',
        'bacterial_gill_disease',
        'fungal_saprolegniasis',
        'parasitic_disease',
        'white_tail_disease',
        'healthy'
    ]

    # --- Label dalam Bahasa Indonesia ---
    DISEASE_LABELS = {
        'bacterial_red_disease': 'Penyakit Merah (Bacterial Red Disease)',
        'aeromonas': 'Aeromonas',
        'bacterial_gill_disease': 'Penyakit Insang Bakteri (Bacterial Gill Disease)',
        'fungal_saprolegniasis': 'Saprolegniasis (Infeksi Jamur)',
        'parasitic_disease': 'Penyakit Parasit',
        'white_tail_disease': 'Penyakit Ekor Putih (White Tail Disease)',
        'healthy': 'Sehat'
    }


class DevelopmentConfig(Config):
    """Konfigurasi untuk lingkungan development."""
    DEBUG = True


class ProductionConfig(Config):
    """Konfigurasi untuk lingkungan production (Railway/PythonAnywhere)."""
    DEBUG = False

    # Keamanan
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Upload lebih ketat di production
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # 3 MB


class TestingConfig(Config):
    """Konfigurasi untuk lingkungan testing."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


# Dictionary untuk memilih konfigurasi berdasarkan environment
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

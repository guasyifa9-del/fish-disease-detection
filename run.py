"""
Entry point untuk menjalankan aplikasi Flask
Fish Disease Detection System.

Cara menjalankan (local):
    python run.py

Untuk production (Railway/Heroku) menggunakan gunicorn:
    gunicorn run:app --bind 0.0.0.0:$PORT
"""

import os
from app import create_app

# Ambil konfigurasi dari environment, default: development
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # PORT dari environment variable (Railway set otomatis)
    port = int(os.environ.get('PORT', 5000))

    print("=" * 50)
    print(" Fish Disease Detection System")
    print(f" Mode: {config_name}")
    print(f" URL : http://127.0.0.1:{port}")
    print("=" * 50)
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', True)
    )

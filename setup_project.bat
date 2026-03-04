@echo off
REM ============================================
REM Fish Disease Detection - Project Setup Script
REM ============================================
REM Membuat seluruh struktur folder proyek
REM secara otomatis.
REM ============================================

echo ============================================
echo  Fish Disease Detection - Setup Project
echo ============================================
echo.

REM --- Direktori utama aplikasi Flask ---
echo [1/6] Membuat struktur app/...
mkdir app 2>nul
mkdir app\static 2>nul
mkdir app\static\css 2>nul
mkdir app\static\js 2>nul
mkdir app\static\images 2>nul
mkdir app\static\uploads 2>nul
mkdir app\templates 2>nul
mkdir app\ml 2>nul

REM --- Direktori model CNN ---
echo [2/6] Membuat direktori models/...
mkdir models 2>nul

REM --- Direktori notebook Jupyter ---
echo [3/6] Membuat direktori notebooks/...
mkdir notebooks 2>nul

REM --- Direktori dataset ---
echo [4/6] Membuat struktur data/...
mkdir data 2>nul
mkdir data\raw 2>nul
mkdir data\processed 2>nul
mkdir data\splits 2>nul
mkdir data\splits\train 2>nul
mkdir data\splits\val 2>nul
mkdir data\splits\test 2>nul

REM --- Direktori database SQLite ---
echo [5/6] Membuat direktori database/...
mkdir database 2>nul

REM --- Membuat file __init__.py ---
echo [6/6] Membuat file-file __init__.py...
if not exist "app\__init__.py" type nul > "app\__init__.py"
if not exist "app\ml\__init__.py" type nul > "app\ml\__init__.py"

REM --- Membuat file .gitkeep untuk folder kosong ---
echo. > models\.gitkeep
echo. > notebooks\.gitkeep
echo. > data\raw\.gitkeep
echo. > data\processed\.gitkeep
echo. > data\splits\train\.gitkeep
echo. > data\splits\val\.gitkeep
echo. > data\splits\test\.gitkeep
echo. > database\.gitkeep
echo. > app\static\uploads\.gitkeep
echo. > app\static\images\.gitkeep

echo.
echo ============================================
echo  Struktur proyek berhasil dibuat!
echo ============================================
echo.
echo Struktur folder:
echo.
echo fish-disease-detection/
echo +-- app/
echo ^|   +-- __init__.py
echo ^|   +-- routes.py
echo ^|   +-- models.py
echo ^|   +-- utils.py
echo ^|   +-- static/
echo ^|   ^|   +-- css/
echo ^|   ^|   +-- js/
echo ^|   ^|   +-- images/
echo ^|   ^|   +-- uploads/
echo ^|   +-- templates/
echo ^|   ^|   +-- base.html
echo ^|   ^|   +-- index.html
echo ^|   ^|   +-- upload.html
echo ^|   ^|   +-- result.html
echo ^|   ^|   +-- history.html
echo ^|   ^|   +-- disease_info.html
echo ^|   +-- ml/
echo ^|       +-- __init__.py
echo ^|       +-- preprocessing.py
echo ^|       +-- model_loader.py
echo ^|       +-- inference.py
echo +-- models/
echo +-- notebooks/
echo +-- data/
echo ^|   +-- raw/
echo ^|   +-- processed/
echo ^|   +-- splits/
echo ^|       +-- train/
echo ^|       +-- val/
echo ^|       +-- test/
echo +-- database/
echo +-- config.py
echo +-- run.py
echo +-- requirements.txt
echo.
echo Langkah selanjutnya:
echo   1. pip install -r requirements.txt
echo   2. python run.py
echo.
pause

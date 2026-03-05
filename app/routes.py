"""
Routes / Endpoint — Fish Disease Detection System.

Arsitektur endpoint mengikuti sequence diagram:
    GET  /                     → halaman landing (index.html)
    GET  /upload               → halaman upload gambar (upload.html)
    POST /predict              → proses deteksi, return JSON hasil
    GET  /result/<id>          → halaman hasil deteksi (result.html)
    GET  /history              → riwayat deteksi (history.html)
    GET  /disease-info/<name>  → info detail penyakit (disease_info.html)
    GET  /api/diseases         → JSON list semua penyakit (untuk AJAX)
    GET  /health               → health check endpoint

Model ERD:
    users ──< detections ──< detection_details >── diseases
"""

import os
import uuid
import logging
import mimetypes
from datetime import datetime
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, jsonify, abort
)
from werkzeug.utils import secure_filename
from app import db, is_model_available
from app.models import Detection, Disease, DetectionDetail
from app.utils import save_detection, get_detection_history

logger = logging.getLogger(__name__)

# Blueprint utama
main_bp = Blueprint('main', __name__)

# ============================================================
# Konstanta Validasi
# ============================================================
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png'}
ALLOWED_MIMETYPES = {'image/jpeg', 'image/png'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


# ============================================================
# Helper Functions
# ============================================================

def _allowed_file(filename):
    """
    Validasi ekstensi file yang diperbolehkan.

    Args:
        filename (str): Nama file yang diupload

    Returns:
        bool: True jika ekstensi diperbolehkan (jpg, jpeg, png)
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def _validate_mime_type(file):
    """
    Validasi MIME type file, bukan hanya ekstensi.
    Mencegah upload file berbahaya yang hanya mengganti ekstensi.

    Args:
        file: FileStorage object dari Flask request

    Returns:
        tuple: (is_valid: bool, mime_type: str)
    """
    # Baca header file untuk deteksi MIME type
    file.seek(0)
    header = file.read(16)
    file.seek(0)  # Reset posisi baca

    # Cek magic bytes
    # JPEG: FF D8 FF
    # PNG:  89 50 4E 47 (‰PNG)
    if header[:3] == b'\xff\xd8\xff':
        return True, 'image/jpeg'
    elif header[:4] == b'\x89PNG':
        return True, 'image/png'
    else:
        return False, 'unknown'


def _save_upload_file(file):
    """
    Simpan file upload ke app/static/uploads/ dengan nama unik (UUID).

    Args:
        file: FileStorage object dari Flask request

    Returns:
        tuple: (filepath_abs, filename)
            - filepath_abs (str): Path absolut ke file yang disimpan
            - filename (str): Nama file unik yang digunakan

    Raises:
        IOError: Jika gagal menyimpan file
    """
    # Ambil ekstensi asli
    original_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'

    # Buat nama unik dengan UUID
    unique_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{original_ext}"
    filename = secure_filename(unique_name)

    # Simpan ke folder uploads
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    logger.info(f"File disimpan: {filename} ({os.path.getsize(filepath)} bytes)")

    return filepath, filename


# ============================================================
# ROUTE: GET / — Halaman Landing
# ============================================================

@main_bp.route('/')
def index():
    """
    Halaman utama / landing page.
    Menampilkan statistik total deteksi dan daftar penyakit.
    """
    try:
        total_detections = Detection.query.count()
        diseases = Disease.query.filter(Disease.disease_name != 'healthy').all()
    except Exception as e:
        logger.error(f"Error loading index data: {e}")
        total_detections = 0
        diseases = []

    return render_template(
        'index.html',
        total_predictions=total_detections,
        diseases=diseases
    )


# ============================================================
# ROUTE: GET /upload — Halaman Upload
# ============================================================

@main_bp.route('/upload')
def upload():
    """
    Halaman upload gambar ikan untuk deteksi.
    Form akan mengirim POST ke /predict.
    """
    return render_template('upload.html')


# ============================================================
# ROUTE: POST /predict — Proses Deteksi (JSON response)
# ============================================================

@main_bp.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint utama untuk memproses deteksi penyakit ikan.

    Pipeline:
        1. Terima file gambar dari form upload
        2. Validasi format (jpg/png/jpeg), MIME type, dan ukuran (max 5MB)
        3. Simpan file ke app/static/uploads/ dengan nama unik (UUID)
        4. Panggil preprocess_image() dari app/ml/preprocessing.py
        5. Panggil predict_disease() dari app/ml/inference.py
        6. Simpan hasil ke database (tabel detections + detection_details)
        7. Return JSON hasil prediksi

    Returns:
        JSON: {status, detection_id, class_name, confidence, redirect_url}
        Atau: {status: "error", message: str} dengan HTTP 400/500
    """
    # --- 1. Cek ketersediaan model CNN ---
    if not is_model_available():
        logger.warning("Predict request ditolak: model belum tersedia")
        return jsonify({
            'status': 'error',
            'message': 'Model CNN belum tersedia. '
                       'Silakan latih model terlebih dahulu dan simpan '
                       'sebagai best_model.h5 di folder models/.'
        }), 503

    # --- 2. Validasi: apakah file ada? ---
    if 'file' not in request.files:
        return jsonify({
            'status': 'error',
            'message': 'Tidak ada file yang dikirim. '
                       'Gunakan key "file" pada form upload.'
        }), 400

    file = request.files['file']

    # Validasi: nama file kosong?
    if file.filename == '' or file.filename is None:
        return jsonify({
            'status': 'error',
            'message': 'Tidak ada file yang dipilih.'
        }), 400

    # --- 3. Validasi ekstensi file ---
    if not _allowed_file(file.filename):
        return jsonify({
            'status': 'error',
            'message': f'Format file tidak didukung. '
                       f'Gunakan: {", ".join(ALLOWED_EXTENSIONS).upper()}.'
        }), 400

    # --- 4. Validasi MIME type (cek isi file, bukan hanya ekstensi) ---
    is_valid_mime, mime_type = _validate_mime_type(file)
    if not is_valid_mime:
        logger.warning(f"MIME type ditolak: {mime_type} untuk {file.filename}")
        return jsonify({
            'status': 'error',
            'message': 'File bukan gambar yang valid. '
                       'Pastikan file adalah JPG atau PNG asli.'
        }), 400

    # --- 5. Validasi ukuran file (max 5MB) ---
    file.seek(0, 2)  # Seek ke akhir file
    file_size = file.tell()
    file.seek(0)  # Reset ke awal

    if file_size > MAX_FILE_SIZE:
        size_mb = file_size / (1024 * 1024)
        return jsonify({
            'status': 'error',
            'message': f'Ukuran file terlalu besar ({size_mb:.1f} MB). '
                       f'Maksimal 5 MB.'
        }), 400

    # --- 6. Simpan file ke uploads/ ---
    try:
        filepath, filename = _save_upload_file(file)
    except Exception as e:
        logger.error(f"Gagal menyimpan file upload: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Gagal menyimpan file. Silakan coba lagi.'
        }), 500

    # --- 7. Jalankan inferensi ML ---
    try:
        logger.info(f"Memulai prediksi untuk: {filename}")

        # Preprocessing + prediksi
        from app.ml.inference import predict_disease
        result = predict_disease(filepath)

        logger.info(
            f"Prediksi selesai: {result['class_name']} "
            f"(confidence: {result['confidence']:.2f}%)"
        )

        # --- 8. Simpan hasil ke database ---
        detection = save_detection(
            image_path=filename,
            predicted_class=result.get('disease_key', result['class_name']),
            confidence=result['confidence'] / 100.0  # Konversi % ke 0-1
        )

        # --- 9. Return JSON response ---
        redirect_url = url_for('main.result', detection_id=detection.detection_id)

        return jsonify({
            'status': 'success',
            'detection_id': detection.detection_id,
            'class_name': result['class_name'],
            'class_name_en': result.get('class_name_en', ''),
            'confidence': result['confidence'],
            'all_probabilities': result.get('all_probabilities', {}),
            'redirect_url': redirect_url
        })

    except FileNotFoundError as e:
        logger.error(f"Model tidak ditemukan: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Model CNN tidak ditemukan. Pastikan best_model.h5 ada.'
        }), 500

    except RuntimeError as e:
        logger.error(f"Runtime error saat prediksi: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

    except Exception as e:
        logger.error(f"Error saat prediksi: {e}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Terjadi kesalahan saat memproses gambar: {str(e)}'
        }), 500


# ============================================================
# ROUTE: GET /result/<id> — Halaman Hasil Deteksi
# ============================================================

@main_bp.route('/result/<int:detection_id>')
def result(detection_id):
    """
    Halaman hasil deteksi penyakit ikan.
    Menampilkan gambar, hasil prediksi, confidence, dan info penyakit.

    Args:
        detection_id (int): ID deteksi dari database
    """
    detection = Detection.query.get_or_404(detection_id)

    # Ambil informasi penyakit dari database
    disease_info = Disease.query.filter_by(
        disease_name=detection.predicted_class
    ).first()

    # Fallback: coba cari berdasarkan nama display jika tidak ketemu
    if not disease_info:
        # Mapping display name ke disease_key
        name_to_key = {
            'Aeromonas (Aeromoniasis)': 'aeromonas',
            'Bacterial Gill Disease (Penyakit Insang)': 'bacterial_gill_disease',
            'Bacterial Red Disease (Bercak Merah)': 'bacterial_red_disease',
            'Fungal Saprolegniasis (Penyakit Jamur)': 'fungal_saprolegniasis',
            'Parasitic Disease (Penyakit Parasit)': 'parasitic_disease',
            'White Tail Disease (Ekor Putih)': 'white_tail_disease',
            'Ikan Sehat': 'healthy',
        }
        key = name_to_key.get(detection.predicted_class, '')
        if key:
            disease_info = Disease.query.filter_by(disease_name=key).first()

    # Label untuk tampilan
    disease_label = detection.predicted_class

    # Coba re-run inferensi untuk mendapatkan probabilitas semua kelas
    probabilities = []
    try:
        if is_model_available():
            import os
            upload_folder = current_app.config['UPLOAD_FOLDER']
            image_full_path = os.path.join(upload_folder, detection.image_filename)

            if os.path.exists(image_full_path):
                from app.ml.inference import predict_disease
                result_data = predict_disease(image_full_path)

                # Ubah dict menjadi sorted list of tuples [(name, prob), ...]
                all_probs = result_data.get('all_probabilities', {})
                probabilities = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)
    except Exception as e:
        current_app.logger.warning(f"Gagal load probabilities: {e}")
        probabilities = []

    return render_template(
        'result.html',
        prediction=detection,
        disease_info=disease_info,
        disease_label=disease_label,
        probabilities=probabilities
    )


# ============================================================
# ROUTE: GET /history — Riwayat Deteksi
# ============================================================

@main_bp.route('/history')
def history():
    """
    Halaman riwayat deteksi penyakit ikan.
    Menampilkan 20 deteksi terbaru, join dengan tabel diseases.
    """
    page = request.args.get('page', 1, type=int)
    per_page = 20

    # Query deteksi terbaru, join dengan diseases untuk nama lengkap
    predictions = Detection.query.order_by(
        Detection.detection_date.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    # Buat mapping disease_name → Disease object untuk info lengkap
    diseases_map = {}
    all_diseases = Disease.query.all()
    for d in all_diseases:
        diseases_map[d.disease_name] = d

    return render_template(
        'history.html',
        predictions=predictions,
        diseases_map=diseases_map,
        disease_labels=current_app.config.get('DISEASE_LABELS', {})
    )


# ============================================================
# ROUTE: GET /disease-info/<name> — Info Detail Penyakit
# ============================================================

@main_bp.route('/disease-info/<string:disease_name>')
@main_bp.route('/disease/<string:disease_name>')  # backward compatible
def disease_info(disease_name):
    """
    Halaman informasi detail penyakit ikan.
    Menampilkan deskripsi, penyebab, gejala, pengobatan, dan pencegahan.

    Args:
        disease_name (str): Nama penyakit (key dari tabel diseases)
    """
    disease = Disease.query.filter_by(disease_name=disease_name).first_or_404()

    # Semua penyakit untuk sidebar navigasi
    all_diseases = Disease.query.all()

    # Ambil 5 deteksi terkait penyakit ini
    related_predictions = Detection.query.filter_by(
        predicted_class=disease_name
    ).order_by(Detection.detection_date.desc()).limit(5).all()

    return render_template(
        'disease_info.html',
        disease=disease,
        all_diseases=all_diseases,
        related_predictions=related_predictions
    )


# ============================================================
# ROUTE: GET /api/diseases — JSON List Semua Penyakit (AJAX)
# ============================================================

@main_bp.route('/api/diseases')
def api_diseases():
    """
    API endpoint yang mengembalikan list semua penyakit dalam format JSON.
    Digunakan oleh frontend untuk AJAX request.

    Returns:
        JSON: {
            "status": "success",
            "count": int,
            "diseases": [
                {
                    "disease_id": int,
                    "disease_name": str,
                    "display_name": str,
                    "cause": str,
                    "symptoms": str,
                    "treatment": str,
                    "prevention": str
                }, ...
            ]
        }
    """
    try:
        diseases = Disease.query.all()

        diseases_list = []
        for d in diseases:
            diseases_list.append({
                'disease_id': d.disease_id,
                'disease_name': d.disease_name,
                'display_name': d.display_name if hasattr(d, 'display_name') else d.disease_name,
                'cause': d.cause if hasattr(d, 'cause') else '',
                'symptoms': d.symptoms if hasattr(d, 'symptoms') else '',
                'treatment': d.treatment if hasattr(d, 'treatment') else '',
                'prevention': d.prevention if hasattr(d, 'prevention') else ''
            })

        return jsonify({
            'status': 'success',
            'count': len(diseases_list),
            'diseases': diseases_list
        })

    except Exception as e:
        logger.error(f"Error fetching diseases: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Gagal mengambil data penyakit.'
        }), 500


# ============================================================
# ROUTE: GET /health — Health Check Endpoint
# ============================================================

@main_bp.route('/health')
def health_check():
    """
    Health check endpoint untuk monitoring.
    Mengecek status database dan model CNN.

    Returns:
        JSON: {
            "status": "healthy" | "degraded",
            "timestamp": str,
            "components": {
                "database": "ok" | "error",
                "model": "loaded" | "not_loaded",
                "uptime": str
            }
        }
    """
    components = {}

    # Cek database
    try:
        Detection.query.first()
        components['database'] = 'ok'
    except Exception:
        components['database'] = 'error'

    # Cek model CNN
    components['model'] = 'loaded' if is_model_available() else 'not_loaded'

    # Cek folder uploads
    upload_folder = current_app.config.get('UPLOAD_FOLDER', '')
    components['uploads_folder'] = 'ok' if os.path.exists(upload_folder) else 'missing'

    # Status keseluruhan
    is_healthy = (
        components['database'] == 'ok' and
        components['model'] == 'loaded'
    )

    return jsonify({
        'status': 'healthy' if is_healthy else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'components': components,
        'version': '1.0.0'
    }), 200 if is_healthy else 503


# ============================================================
# ROUTE: GET /api/history — API Riwayat Deteksi (JSON)
# ============================================================

@main_bp.route('/api/history')
def api_history():
    """
    API endpoint untuk riwayat deteksi dalam format JSON.

    Query params:
        limit (int): Jumlah record (default: 50)

    Returns:
        JSON: {"detections": [...]}
    """
    limit = request.args.get('limit', 50, type=int)
    detections = get_detection_history(limit=limit)

    detections_list = []
    for d in detections:
        detections_list.append({
            'detection_id': d.detection_id,
            'image_path': d.image_path,
            'predicted_class': d.predicted_class,
            'confidence_score': d.confidence_score,
            'detection_date': d.detection_date.isoformat() if d.detection_date else None
        })

    return jsonify({
        'status': 'success',
        'count': len(detections_list),
        'detections': detections_list
    })

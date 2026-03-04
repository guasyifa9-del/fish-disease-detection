"""
Fungsi Utilitas untuk Fish Disease Detection System.

Berisi:
  - init_db(app)       → Buat tabel + seed data 7 penyakit
  - save_detection()   → Simpan hasil deteksi ke database
  - get_detection_history() → Ambil riwayat deteksi
  - allowed_file()     → Validasi ekstensi file
  - save_upload()      → Simpan file upload
"""

import os
import uuid
import logging
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

logger = logging.getLogger(__name__)


# ============================================================
# Fungsi Upload
# ============================================================
def allowed_file(filename):
    """
    Memeriksa apakah ekstensi file diperbolehkan.

    Args:
        filename (str): Nama file yang akan diperiksa

    Returns:
        bool: True jika ekstensi diperbolehkan, False jika tidak
    """
    if '.' not in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in current_app.config.get('ALLOWED_EXTENSIONS', set())


def save_upload(file):
    """
    Menyimpan file upload ke folder uploads dengan nama unik.

    Args:
        file: FileStorage object dari Flask request

    Returns:
        tuple: (filepath, filename) - path absolut dan nama file yang disimpan
    """
    original_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    unique_id = uuid.uuid4().hex[:8]
    filename = f'{timestamp}_{unique_id}.{original_ext}'

    filename = secure_filename(filename)

    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)

    return filepath, filename


# ============================================================
# Fungsi Database
# ============================================================
def init_db(app):
    """
    Menginisialisasi database: membuat semua tabel dan mengisi
    data awal 7 penyakit ikan jika tabel diseases masih kosong.

    Dipanggil dari app/__init__.py saat create_app().

    Args:
        app (Flask): Instance aplikasi Flask
    """
    from app import db
    from app.models import User, Detection, Disease, DetectionDetail  # noqa: F401

    with app.app_context():
        # Buat semua tabel berdasarkan model
        db.create_all()
        logger.info("Tabel database berhasil dibuat/diverifikasi.")

        # Seed data penyakit jika kosong
        _seed_diseases()


def _seed_diseases():
    """
    Mengisi data awal 7 kelas penyakit ikan ke tabel diseases.
    Hanya dijalankan jika tabel masih kosong.

    Data ditulis dalam Bahasa Indonesia yang mudah dipahami
    oleh pembudidaya ikan awam.
    """
    from app import db
    from app.models import Disease

    if Disease.query.count() > 0:
        logger.info("Data penyakit sudah ada di database. Skip seeding.")
        return

    logger.info("Mengisi data awal 7 kelas penyakit ikan...")

    diseases = [
        Disease(
            disease_name='bacterial_red_disease',
            cause=(
                'Disebabkan oleh bakteri Aeromonas hydrophila yang biasanya muncul '
                'ketika kualitas air buruk, kepadatan ikan terlalu tinggi, atau ikan '
                'mengalami stres. Bakteri ini bisa menyebar lewat air yang tercemar '
                'dan luka pada tubuh ikan.'
            ),
            symptoms=(
                'Muncul bercak-bercak merah pada tubuh ikan terutama di bagian perut '
                'dan pangkal sirip. Sirip terlihat geripis atau rontok. Perut ikan '
                'membengkak berisi cairan. Nafsu makan menurun drastis. Ikan menjadi '
                'lesu dan sering berdiam di dasar kolam.'
            ),
            treatment=(
                'Rendam ikan dalam larutan oxytetracycline 5-10 ppm selama 24 jam. '
                'Bisa juga menggunakan kalium permanganat (PK) 2-4 ppm selama 30 menit. '
                'Pisahkan ikan sakit ke kolam karantina. Perbaiki kualitas air segera '
                'dengan pergantian air 30-50%. Berikan pakan yang dicampur antibiotik '
                'selama 5-7 hari.'
            ),
            prevention=(
                'Jaga kualitas air secara rutin: pH 6.5-8.5, suhu 25-30°C, amonia < 0.1 ppm. '
                'Hindari kepadatan ikan berlebih (maks 5-10 ekor/m² tergantung ukuran). '
                'Berikan pakan berkualitas dan jangan berlebihan. Lakukan karantina '
                'ikan baru selama 7-14 hari sebelum digabung. Desinfeksi peralatan '
                'kolam secara berkala.'
            ),
            image_example=None
        ),
        Disease(
            disease_name='aeromonas',
            cause=(
                'Disebabkan oleh bakteri Aeromonas spp. (A. hydrophila, A. sobria, '
                'A. caviae). Bakteri ini hidup alami di air tawar dan menjadi patogen '
                'ketika ikan stres, kualitas air menurun, atau ada luka pada tubuh ikan. '
                'Penularan terjadi melalui kontak langsung dan air yang terkontaminasi.'
            ),
            symptoms=(
                'Luka terbuka atau borok (ulkus) pada kulit ikan. Pendarahan pada '
                'sirip, mulut, dan permukaan tubuh. Perut membengkak berisi cairan '
                '(dropsy/ascites). Sisik berdiri seperti buah pinus (pine cone). '
                'Mata menonjol keluar (exophthalmia/pop-eye). Warna tubuh menjadi '
                'gelap dan kusam.'
            ),
            treatment=(
                'Rendam ikan dalam kalium permanganat (KMnO4) 2-5 ppm selama 30-60 menit. '
                'Berikan antibiotik erythromycin atau enrofloxacin melalui pakan selama '
                '7-10 hari. Oleskan obat merah (povidone iodine) pada luka terbuka. '
                'Tingkatkan aerasi kolam. Ganti air 30-50% setiap hari selama pengobatan.'
            ),
            prevention=(
                'Kontrol kualitas air secara rutin minimal seminggu sekali. '
                'Desinfeksi peralatan sebelum dan sesudah digunakan. Hindari '
                'penanganan kasar yang menyebabkan luka pada ikan. Berikan pakan '
                'bernutrisi seimbang untuk menjaga daya tahan tubuh. Vaksinasi '
                'jika tersedia untuk spesies yang dibudidayakan.'
            ),
            image_example=None
        ),
        Disease(
            disease_name='bacterial_gill_disease',
            cause=(
                'Disebabkan oleh bakteri Flavobacterium branchiophilum dan beberapa '
                'bakteri lain yang menyerang jaringan insang. Biasanya muncul di '
                'kolam dengan kepadatan tinggi, kadar amonia tinggi, dan oksigen '
                'terlarut rendah. Perubahan suhu mendadak juga bisa memicu penyakit ini.'
            ),
            symptoms=(
                'Insang berubah warna menjadi pucat, kecoklatan, atau berwarna gelap. '
                'Terdapat lendir berlebih pada insang. Ikan sering megap-megap di '
                'permukaan air karena kesulitan bernapas. Tutup insang (operkulum) '
                'terbuka lebih lebar dari normal dan bergerak sangat cepat. '
                'Nafsu makan menurun dan pertumbuhan terhambat.'
            ),
            treatment=(
                'Rendam ikan dalam formalin 25-50 ppm selama 30-60 menit (perhatikan '
                'kadar oksigen selama perendaman). Gunakan garam dapur (NaCl) 1-3% '
                'selama 10-30 menit sebagai bath treatment. Perbaiki sirkulasi air '
                'dan tingkatkan aerasi. Kurangi kepadatan ikan jika terlalu padat.'
            ),
            prevention=(
                'Jaga kebersihan air dan pastikan aerasi/oksigen cukup (min 5 mg/L). '
                'Hindari kepadatan kolam berlebihan. Bersihkan filter dan dasar kolam '
                'secara rutin. Monitor kadar amonia dan nitrit (harus < 0.1 ppm). '
                'Hindari perubahan suhu air yang mendadak (maks 2°C per hari).'
            ),
            image_example=None
        ),
        Disease(
            disease_name='fungal_saprolegniasis',
            cause=(
                'Disebabkan oleh jamur Saprolegnia spp. dan Achlya spp. Jamur ini '
                'hidup alami di air dan menyerang ikan yang sudah memiliki luka '
                'atau daya tahan tubuh lemah. Terjadi lebih sering di air bersuhu '
                'rendah (di bawah 20°C) dan saat musim hujan. Telur ikan juga '
                'rentan terinfeksi jamur ini.'
            ),
            symptoms=(
                'Muncul gumpalan mirip kapas putih atau abu-abu pada permukaan tubuh, '
                'sirip, atau insang ikan. Luka pada tubuh yang tidak kunjung sembuh '
                'dan dikelilingi serabut jamur. Ikan menjadi lesu dan tidak aktif. '
                'Warna kulit di sekitar infeksi berubah kemerahan atau pucat. '
                'Sirip rusak dan terurai.'
            ),
            treatment=(
                'Rendam ikan dalam methylene blue 2-3 ppm selama 24 jam. '
                'Gunakan garam dapur (NaCl) 1-3% selama 10-30 menit. '
                'Bisa menggunakan malachite green 0.1 ppm (hati-hati, bersifat '
                'toksik pada dosis tinggi — DILARANG untuk ikan konsumsi di beberapa negara). '
                'Oleskan povidone iodine pada area jamur yang terlihat. '
                'Angkat serabut jamur yang besar secara mekanis dengan hati-hati.'
            ),
            prevention=(
                'Hindari penanganan kasar yang menyebabkan luka pada kulit ikan. '
                'Jaga suhu air tetap stabil, idealnya 25-30°C. Perbaiki kualitas '
                'air dan desinfeksi peralatan secara berkala. Berikan pakan yang '
                'mengandung vitamin C untuk meningkatkan imunitas ikan. '
                'Segera obati luka sekecil apapun pada ikan.'
            ),
            image_example=None
        ),
        Disease(
            disease_name='parasitic_disease',
            cause=(
                'Disebabkan oleh berbagai parasit seperti Ichthyophthirius multifiliis '
                '(penyebab white spot/ich), Trichodina, Dactylogyrus (cacing insang), '
                'dan Argulus (kutu ikan). Parasit berkembang biak pesat di kolam '
                'dengan kebersihan buruk, kepadatan tinggi, dan ikan stres. '
                'Penularan terjadi melalui kontak antar ikan dan air.'
            ),
            symptoms=(
                'Bintik-bintik putih pada tubuh dan sirip (white spot/ich). '
                'Ikan sering menggosokkan tubuhnya ke dinding atau dasar kolam '
                '(flashing). Produksi lendir berlebih sehingga kulit terlihat '
                'berkabut. Pernapasan cepat dan sering megap-megap. Sirip mengatup '
                'dan tidak mengembang normal. Nafsu makan menurun drastis. '
                'Pada serangan berat, ikan kurus dan mati.'
            ),
            treatment=(
                'Untuk white spot: naikkan suhu air secara bertahap ke 28-30°C '
                'untuk mempercepat siklus hidup parasit, lalu obati. '
                'Rendam ikan dalam formalin 25 ppm selama 24 jam. '
                'Gunakan garam 3-5% selama 10-15 menit sebagai bath treatment. '
                'Untuk kutu ikan (Argulus): cabut secara manual dengan pinset dan '
                'obati luka dengan povidone iodine. '
                'Untuk cacing insang: gunakan praziquantel 2-10 ppm.'
            ),
            prevention=(
                'Karantina ikan baru selama 7-14 hari sebelum digabung ke kolam utama. '
                'Jaga kualitas air dan kebersihan kolam. Hindari stres pada ikan '
                '(perubahan suhu mendadak, penanganan berlebihan). Berikan pakan '
                'bernutrisi tinggi untuk menjaga daya tahan tubuh. Periksa ikan '
                'secara rutin untuk mendeteksi parasit sejak dini.'
            ),
            image_example=None
        ),
        Disease(
            disease_name='white_tail_disease',
            cause=(
                'Disebabkan oleh bakteri Flexibacter columnaris (Flavobacterium '
                'columnare) atau dalam beberapa kasus oleh infeksi virus. '
                'Penyakit ini sering muncul pada ikan muda dan larva. '
                'Faktor pemicu meliputi suhu air tinggi (>28°C), kepadatan '
                'berlebih, kualitas air rendah, dan stres akibat penanganan.'
            ),
            symptoms=(
                'Bagian ekor dan sirip ekor berubah warna menjadi putih atau keputihan. '
                'Terjadi erosi dan kerusakan pada sirip ekor yang makin parah. '
                'Gerakan renang tidak normal — ikan berenang miring atau berputar-putar. '
                'Ikan cenderung berkumpul di permukaan atau di sudut kolam. '
                'Nafsu makan menurun dan pertumbuhan terhambat. '
                'Pada kasus parah, ekor bisa terputus seluruhnya.'
            ),
            treatment=(
                'Rendam ikan dalam oxytetracycline 10-50 ppm selama 1 jam. '
                'Bisa juga menggunakan garam 1-2% selama 10-15 menit. '
                'Isolasi ikan yang terinfeksi segera ke kolam terpisah. '
                'Gunakan antibiotik melalui pakan (oxytetracycline 50 mg/kg pakan) '
                'selama 7-10 hari. Perbaiki kualitas air secara menyeluruh.'
            ),
            prevention=(
                'Jaga suhu air tetap stabil, idealnya 25-28°C. '
                'Hindari kepadatan ikan berlebihan terutama untuk ikan muda. '
                'Desinfeksi perlengkapan dan peralatan budidaya secara teratur. '
                'Jaga kebersihan kolam dan lakukan pergantian air rutin. '
                'Tangani ikan dengan lembut untuk menghindari stres dan luka.'
            ),
            image_example=None
        ),
        Disease(
            disease_name='healthy',
            cause=(
                'Ikan dalam kondisi sehat, tidak terinfeksi bakteri, jamur, '
                'virus, atau parasit. Kondisi ini menunjukkan lingkungan '
                'budidaya yang baik dan manajemen kolam yang benar.'
            ),
            symptoms=(
                'Tidak ada tanda-tanda penyakit. Ikan aktif berenang dengan gerakan '
                'normal dan lincah. Nafsu makan baik dan respon cepat terhadap pakan. '
                'Warna tubuh cerah dan mengkilap sesuai spesiesnya. Sirip terbuka '
                'sempurna tanpa kerusakan. Insang berwarna merah segar. '
                'Pertumbuhan normal sesuai umur.'
            ),
            treatment=(
                'Tidak diperlukan pengobatan. Lanjutkan pemeliharaan rutin '
                'dan pertahankan kualitas air yang sudah baik. Berikan pakan '
                'secara teratur dengan komposisi nutrisi seimbang.'
            ),
            prevention=(
                'Jaga kualitas air secara konsisten: pH 6.5-8.5, suhu 25-30°C, '
                'oksigen terlarut > 5 mg/L, amonia < 0.1 ppm. Berikan pakan '
                'teratur dan bernutrisi seimbang (protein 25-35% untuk ikan dewasa). '
                'Kontrol kepadatan kolam agar tidak berlebihan. Lakukan pemeriksaan '
                'kesehatan ikan secara rutin minimal seminggu sekali. '
                'Pergantian air rutin 10-20% per minggu.'
            ),
            image_example=None
        ),
    ]

    db.session.add_all(diseases)
    db.session.commit()
    logger.info(f"Berhasil menambahkan {len(diseases)} data penyakit ke database.")


# ============================================================
# Fungsi Deteksi
# ============================================================
def save_detection(image_path, predicted_class, confidence, disease_id=None,
                   user_id=None, notes=None):
    """
    Menyimpan hasil deteksi penyakit ikan ke database.

    Args:
        image_path (str): Path file gambar yang dideteksi
        predicted_class (str): Nama kelas penyakit hasil prediksi
        confidence (float): Skor keyakinan (0.0 - 1.0)
        disease_id (int, optional): ID penyakit di tabel diseases
        user_id (int, optional): ID user (None untuk guest)
        notes (str, optional): Catatan tambahan

    Returns:
        Detection: Object deteksi yang berhasil disimpan
    """
    from app import db
    from app.models import Detection, DetectionDetail, Disease

    # Buat record deteksi
    detection = Detection(
        user_id=user_id,
        image_path=image_path,
        predicted_class=predicted_class,
        confidence_score=confidence
    )
    db.session.add(detection)
    db.session.flush()  # Agar detection_id ter-generate

    # Cari disease_id otomatis jika tidak diberikan
    if disease_id is None:
        disease = Disease.query.filter_by(disease_name=predicted_class).first()
        if disease:
            disease_id = disease.disease_id

    # Buat detection_detail jika disease_id ditemukan
    if disease_id is not None:
        detail = DetectionDetail(
            detection_id=detection.detection_id,
            disease_id=disease_id,
            notes=notes or f'Hasil deteksi otomatis: {predicted_class} '
                           f'(confidence: {confidence:.2%})'
        )
        db.session.add(detail)

    db.session.commit()
    logger.info(
        f"Deteksi disimpan: ID={detection.detection_id}, "
        f"class={predicted_class}, confidence={confidence:.4f}"
    )

    return detection


def get_detection_history(limit=20, user_id=None):
    """
    Mengambil riwayat deteksi penyakit ikan dari database.

    Args:
        limit (int): Jumlah maksimum record yang dikembalikan (default: 20)
        user_id (int, optional): Filter berdasarkan user_id.
            Jika None, ambil semua deteksi.

    Returns:
        list[Detection]: List object Detection terurut dari terbaru
    """
    from app.models import Detection

    query = Detection.query.order_by(Detection.detection_date.desc())

    # Filter per user jika diberikan
    if user_id is not None:
        query = query.filter_by(user_id=user_id)

    detections = query.limit(limit).all()

    return detections


# ============================================================
# Fungsi Tambahan
# ============================================================
def get_disease_info(disease_name):
    """
    Mengambil informasi lengkap penyakit berdasarkan nama kelas.

    Args:
        disease_name (str): Nama kelas penyakit (contoh: 'bacterial_red_disease')

    Returns:
        dict: Dictionary berisi informasi penyakit, atau None jika tidak ditemukan
    """
    from app.models import Disease

    disease = Disease.query.filter_by(disease_name=disease_name).first()
    if disease:
        return disease.to_dict()
    return None


def format_confidence(confidence):
    """
    Memformat nilai confidence menjadi string persentase.

    Args:
        confidence (float): Nilai confidence (0.0 - 1.0)

    Returns:
        str: String persentase (contoh: '95.23%')
    """
    return f'{confidence * 100:.2f}%'


def get_detection_stats():
    """
    Menghitung statistik deteksi.

    Returns:
        dict: Statistik deteksi (total, per penyakit)
    """
    from app import db
    from app.models import Detection
    from sqlalchemy import func

    total = Detection.query.count()

    # Hitung per kelas penyakit
    results = db.session.query(
        Detection.predicted_class,
        func.count(Detection.detection_id).label('count')
    ).group_by(Detection.predicted_class).all()

    by_disease = [{'disease': r.predicted_class, 'count': r.count} for r in results]

    return {
        'total_detections': total,
        'by_disease': by_disease
    }


def cleanup_old_uploads(days=30):
    """
    Menghapus file upload yang lebih lama dari jumlah hari tertentu.

    Args:
        days (int): Jumlah hari. File lebih lama dari ini akan dihapus.

    Returns:
        int: Jumlah file yang dihapus
    """
    upload_folder = current_app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_folder):
        return 0

    now = datetime.now()
    deleted_count = 0

    for filename in os.listdir(upload_folder):
        filepath = os.path.join(upload_folder, filename)
        if os.path.isfile(filepath) and filename != '.gitkeep':
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if (now - file_time).days > days:
                os.remove(filepath)
                deleted_count += 1

    return deleted_count

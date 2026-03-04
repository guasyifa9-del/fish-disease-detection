"""
Inference Pipeline — Menjalankan prediksi penyakit ikan.
Fish Disease Detection System.

Module ini menangani seluruh pipeline inferensi:
- Preprocessing gambar
- Prediksi menggunakan model CNN
- Decode hasil ke label kelas (Bahasa Indonesia)
- Return hasil dalam format dictionary

Mapping 7 kelas penyakit:
    0: Bacterial Red Disease (Bercak Merah)
    1: Aeromonas (Aeromoniasis)
    2: Bacterial Gill Disease (Penyakit Insang)
    3: Fungal Saprolegniasis (Penyakit Jamur)
    4: Parasitic Disease (Penyakit Parasit)
    5: White Tail Disease (Ekor Putih)
    6: Ikan Sehat
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Mapping class_id ke nama penyakit
# Urutan ini HARUS sesuai dengan output model (flow_from_directory)
# flow_from_directory mengurutkan folder secara ALFABETIS
# ============================================================

CLASS_NAMES = {
    0: {
        'folder': 'bacterial_Aeromoniasis',
        'name': 'Aeromonas (Aeromoniasis)',
        'name_en': 'Aeromonas'
    },
    1: {
        'folder': 'bacterial_gill_disease',
        'name': 'Bacterial Gill Disease (Penyakit Insang)',
        'name_en': 'Bacterial Gill Disease'
    },
    2: {
        'folder': 'bacterial_red_disease',
        'name': 'Bacterial Red Disease (Bercak Merah)',
        'name_en': 'Bacterial Red Disease'
    },
    3: {
        'folder': 'fungal_disease',
        'name': 'Fungal Saprolegniasis (Penyakit Jamur)',
        'name_en': 'Fungal Saprolegniasis'
    },
    4: {
        'folder': 'healthy',
        'name': 'Ikan Sehat',
        'name_en': 'Healthy'
    },
    5: {
        'folder': 'parasitic_disease',
        'name': 'Parasitic Disease (Penyakit Parasit)',
        'name_en': 'Parasitic Disease'
    },
    6: {
        'folder': 'white_tail_disease',
        'name': 'White Tail Disease (Ekor Putih)',
        'name_en': 'White Tail Disease'
    }
}

NUM_CLASSES = len(CLASS_NAMES)


def predict_disease(image_path, model=None):
    """
    Pipeline lengkap untuk memprediksi penyakit ikan dari gambar.

    Pipeline:
        1. Panggil preprocess_image() — resize, normalize, expand dims
        2. Jalankan model.predict() — inferensi CNN
        3. Ambil class dengan probabilitas tertinggi
        4. Return dictionary hasil prediksi

    Args:
        image_path (str): Path absolut ke file gambar ikan.
            Format: PNG, JPG, JPEG, BMP, WEBP
        model (tensorflow.keras.Model, optional): Model CNN.
            Jika None, akan mengambil dari singleton di app/__init__.py

    Returns:
        dict: Hasil prediksi dengan keys:
            - 'class_id' (int): Index kelas (0-6)
            - 'class_name' (str): Nama penyakit dalam Bahasa Indonesia
            - 'class_name_en' (str): Nama penyakit dalam Bahasa Inggris
            - 'confidence' (float): Tingkat keyakinan (0-100%)
            - 'all_probabilities' (dict): Probabilitas semua 7 kelas
                {nama_kelas: probabilitas_persen}

    Raises:
        FileNotFoundError: Jika file gambar tidak ditemukan
        RuntimeError: Jika model CNN belum tersedia
        Exception: Jika terjadi error saat inferensi
    """
    # 1. Preprocessing gambar
    from app.ml.preprocessing import preprocess_image
    logger.info(f"Memulai prediksi untuk: {image_path}")
    processed_image = preprocess_image(image_path)

    # 2. Load model (singleton)
    if model is None:
        from app.ml.model_loader import get_model
        model = get_model()

    # 3. Prediksi
    logger.info("Menjalankan inferensi CNN...")
    predictions = model.predict(processed_image, verbose=0)
    prediction_array = predictions[0]  # Ambil batch pertama

    # 4. Decode hasil
    class_id = int(np.argmax(prediction_array))
    confidence = float(prediction_array[class_id]) * 100  # Konversi ke persen

    # Ambil info kelas
    class_info = CLASS_NAMES.get(class_id, {
        'folder': f'unknown_{class_id}',
        'name': f'Tidak Dikenal (ID: {class_id})',
        'name_en': f'Unknown (ID: {class_id})'
    })

    # Buat dictionary probabilitas semua kelas
    all_probabilities = {}
    for idx in range(min(NUM_CLASSES, len(prediction_array))):
        cls = CLASS_NAMES.get(idx)
        if cls:
            all_probabilities[cls['name']] = round(
                float(prediction_array[idx]) * 100, 2
            )

    # Urutkan berdasarkan probabilitas (tertinggi dulu)
    all_probabilities = dict(
        sorted(all_probabilities.items(), key=lambda x: x[1], reverse=True)
    )

    result = {
        'class_id': class_id,
        'class_name': class_info['name'],
        'class_name_en': class_info['name_en'],
        'confidence': round(confidence, 2),
        'all_probabilities': all_probabilities
    }

    logger.info(
        f"Hasil prediksi: {result['class_name']} "
        f"(confidence: {result['confidence']:.2f}%)"
    )

    return result


def predict_top_k(image_path, k=3, model=None):
    """
    Mendapatkan top-K prediksi untuk sebuah gambar.

    Berguna untuk menampilkan beberapa kemungkinan diagnosis,
    bukan hanya kelas dengan probabilitas tertinggi.

    Args:
        image_path (str): Path ke file gambar ikan
        k (int): Jumlah prediksi teratas (default: 3)
        model (tensorflow.keras.Model, optional): Model CNN

    Returns:
        list[dict]: List of dict, diurutkan dari confidence tertinggi.
            Setiap dict berisi:
            - 'class_id' (int): Index kelas
            - 'class_name' (str): Nama penyakit (Indonesia)
            - 'confidence' (float): Confidence dalam persen (0-100%)
    """
    from app.ml.preprocessing import preprocess_image
    from app.ml.model_loader import get_model as _get_model

    processed_image = preprocess_image(image_path)

    if model is None:
        model = _get_model()

    predictions = model.predict(processed_image, verbose=0)
    prediction_array = predictions[0]

    # Ambil top-K indices (descending)
    top_indices = np.argsort(prediction_array)[::-1][:k]

    results = []
    for idx in top_indices:
        idx = int(idx)
        class_info = CLASS_NAMES.get(idx, {
            'name': f'Tidak Dikenal (ID: {idx})',
            'name_en': f'Unknown (ID: {idx})'
        })
        results.append({
            'class_id': idx,
            'class_name': class_info['name'],
            'class_name_en': class_info.get('name_en', ''),
            'confidence': round(float(prediction_array[idx]) * 100, 2)
        })

    return results


def get_class_names():
    """
    Mengembalikan dictionary mapping class_id ke nama kelas.

    Returns:
        dict: {class_id: {'folder': str, 'name': str, 'name_en': str}}
    """
    return CLASS_NAMES.copy()

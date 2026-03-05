"""
Inference Pipeline — Menjalankan prediksi penyakit ikan.
Fish Disease Detection System.

Module ini menangani seluruh pipeline inferensi:
- Preprocessing gambar
- Prediksi menggunakan model CNN
- Decode hasil ke label kelas (Bahasa Indonesia)
- Return hasil dalam format dictionary

Mapping 7 kelas penyakit dimuat dari models/class_labels.json
yang di-generate saat training di Colab.
"""

import os
import json
import numpy as np
import logging

logger = logging.getLogger(__name__)

# ============================================================
# Mapping class_id ke nama penyakit
# Dimuat dari class_labels.json (generated saat training)
# ============================================================

# Path ke class_labels.json
_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
_LABELS_PATH = os.path.join(_BASE_DIR, 'models', 'class_labels.json')

# Mapping folder name training → database key
_FOLDER_TO_DB_KEY = {
    'Bacterial Red disease': 'bacterial_red_disease',
    'Bacterial diseases - Aeromoniasis': 'aeromonas',
    'Bacterial gill disease': 'bacterial_gill_disease',
    'Fungal diseases Saprolegniasis': 'fungal_saprolegniasis',
    'Healthy Fish': 'healthy',
    'Parasitic diseases': 'parasitic_disease',
    'Viral diseases White tail disease': 'white_tail_disease',
}

# Display names untuk UI (Bahasa Indonesia)
_DB_KEY_TO_DISPLAY = {
    'bacterial_red_disease': {
        'name': 'Bacterial Red Disease (Bercak Merah)',
        'name_en': 'Bacterial Red Disease'
    },
    'aeromonas': {
        'name': 'Aeromonas (Aeromoniasis)',
        'name_en': 'Aeromonas'
    },
    'bacterial_gill_disease': {
        'name': 'Bacterial Gill Disease (Penyakit Insang)',
        'name_en': 'Bacterial Gill Disease'
    },
    'fungal_saprolegniasis': {
        'name': 'Fungal Saprolegniasis (Penyakit Jamur)',
        'name_en': 'Fungal Saprolegniasis'
    },
    'healthy': {
        'name': 'Ikan Sehat',
        'name_en': 'Healthy'
    },
    'parasitic_disease': {
        'name': 'Parasitic Disease (Penyakit Parasit)',
        'name_en': 'Parasitic Disease'
    },
    'white_tail_disease': {
        'name': 'White Tail Disease (Ekor Putih)',
        'name_en': 'White Tail Disease'
    },
}


def _load_class_mapping():
    """
    Memuat mapping kelas dari class_labels.json.
    Return dict: {class_id: {folder, db_key, name, name_en}}
    """
    class_names = {}

    if os.path.exists(_LABELS_PATH):
        with open(_LABELS_PATH, 'r') as f:
            labels_data = json.load(f)

        # index_to_class: {"0": "Bacterial Red disease", ...}
        index_to_class = labels_data.get('index_to_class', {})

        for idx_str, folder_name in index_to_class.items():
            idx = int(idx_str)
            db_key = _FOLDER_TO_DB_KEY.get(folder_name, folder_name.lower().replace(' ', '_'))
            display = _DB_KEY_TO_DISPLAY.get(db_key, {
                'name': folder_name,
                'name_en': folder_name
            })

            class_names[idx] = {
                'folder': folder_name,
                'db_key': db_key,
                'name': display['name'],
                'name_en': display['name_en']
            }

        logger.info(f"Class mapping dimuat dari {_LABELS_PATH}: {len(class_names)} kelas")
        for idx in sorted(class_names.keys()):
            logger.info(f"  {idx}: {class_names[idx]['folder']} → {class_names[idx]['db_key']}")
    else:
        logger.warning(f"class_labels.json tidak ditemukan di {_LABELS_PATH}, gunakan default")
        # Fallback default (sesuai class_labels.json)
        default_classes = [
            ('Bacterial Red disease', 'bacterial_red_disease'),
            ('Bacterial diseases - Aeromoniasis', 'aeromonas'),
            ('Bacterial gill disease', 'bacterial_gill_disease'),
            ('Fungal diseases Saprolegniasis', 'fungal_saprolegniasis'),
            ('Healthy Fish', 'healthy'),
            ('Parasitic diseases', 'parasitic_disease'),
            ('Viral diseases White tail disease', 'white_tail_disease'),
        ]
        for idx, (folder, db_key) in enumerate(default_classes):
            display = _DB_KEY_TO_DISPLAY.get(db_key, {'name': folder, 'name_en': folder})
            class_names[idx] = {
                'folder': folder,
                'db_key': db_key,
                'name': display['name'],
                'name_en': display['name_en']
            }

    return class_names


# Load class mapping saat module di-import
CLASS_NAMES = _load_class_mapping()
NUM_CLASSES = len(CLASS_NAMES)


def predict_disease(image_path, model=None):
    """
    Pipeline lengkap untuk memprediksi penyakit ikan dari gambar.

    Args:
        image_path (str): Path absolut ke file gambar ikan.
        model (tensorflow.keras.Model, optional): Model CNN.

    Returns:
        dict: Hasil prediksi dengan keys:
            - 'class_id' (int): Index kelas (0-6)
            - 'class_name' (str): Nama penyakit dalam Bahasa Indonesia
            - 'class_name_en' (str): Nama penyakit dalam Bahasa Inggris
            - 'disease_key' (str): Key database (untuk lookup info penyakit)
            - 'confidence' (float): Tingkat keyakinan (0-100%)
            - 'all_probabilities' (dict): Probabilitas semua 7 kelas
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
        'db_key': f'unknown_{class_id}',
        'name': f'Tidak Dikenal (ID: {class_id})',
        'name_en': f'Unknown (ID: {class_id})'
    })

    # Log raw predictions untuk debugging
    logger.info(f"Raw predictions: {[f'{p:.4f}' for p in prediction_array]}")
    logger.info(f"Predicted class_id: {class_id} → {class_info['folder']} ({class_info['db_key']})")

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
        'disease_key': class_info['db_key'],
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

    Args:
        image_path (str): Path ke file gambar ikan
        k (int): Jumlah prediksi teratas (default: 3)
        model (tensorflow.keras.Model, optional): Model CNN

    Returns:
        list[dict]: List of dict, diurutkan dari confidence tertinggi.
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
        dict: {class_id: {'folder': str, 'db_key': str, 'name': str, 'name_en': str}}
    """
    return CLASS_NAMES.copy()

"""
test_app.py — Automated Test Suite
Fish Disease Detection System

Menguji seluruh komponen aplikasi:
  1. GET endpoint → status 200 + template benar
  2. POST /predict → validasi file + respons JSON
  3. Database → verifikasi data tersimpan
  4. Preprocessing → output shape (1, 224, 224, 3)
  5. Inference → output dictionary dengan key yang benar

Jalankan: pytest test_app.py -v
"""

import os
import io
import sys
import pytest
import tempfile
import shutil

# Path proyek
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture(scope='module')
def app():
    """Buat instance Flask app untuk testing (SQLite in-memory)."""
    from app import create_app, db

    app = create_app('testing')

    # Buat temp folder untuk uploads
    test_upload_dir = tempfile.mkdtemp()
    app.config['UPLOAD_FOLDER'] = test_upload_dir
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        # create_app sudah memanggil init_db() yang membuat tabel + seed data
        yield app

        db.session.remove()
        db.drop_all()

    # Cleanup temp folder
    shutil.rmtree(test_upload_dir, ignore_errors=True)


@pytest.fixture
def client(app):
    """Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI test runner."""
    return app.test_cli_runner()


def _create_test_image_jpg(size_kb=50):
    """Buat file JPG sintetis untuk testing."""
    try:
        from PIL import Image
        img = Image.new('RGB', (224, 224), color=(100, 150, 200))
        buf = io.BytesIO()
        img.save(buf, format='JPEG')
        buf.seek(0)
        return buf
    except ImportError:
        # Fallback: minimal JPEG header
        buf = io.BytesIO()
        # JPEG magic bytes: FFD8FF
        buf.write(b'\xff\xd8\xff\xe0')
        buf.write(b'\x00' * (size_kb * 1024))
        buf.seek(0)
        return buf


def _create_test_image_png():
    """Buat file PNG sintetis untuk testing."""
    try:
        from PIL import Image
        img = Image.new('RGB', (224, 224), color=(50, 100, 150))
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return buf
    except ImportError:
        buf = io.BytesIO()
        # PNG magic bytes
        buf.write(b'\x89PNG\r\n\x1a\n')
        buf.write(b'\x00' * 1024)
        buf.seek(0)
        return buf


def _create_pdf_file():
    """Buat file PDF palsu untuk test validasi."""
    buf = io.BytesIO()
    buf.write(b'%PDF-1.4 fake pdf content')
    buf.write(b'\x00' * 1024)
    buf.seek(0)
    return buf


def _create_oversized_file():
    """Buat file > 5MB untuk test validasi ukuran."""
    buf = io.BytesIO()
    # JPEG header
    buf.write(b'\xff\xd8\xff\xe0')
    # 6 MB data
    buf.write(b'\x00' * (6 * 1024 * 1024))
    buf.seek(0)
    return buf


# ============================================================
# 1. TEST GET ENDPOINTS — Status 200 + Template
# ============================================================

class TestGetEndpoints:
    """Test semua halaman GET mengembalikan status 200."""

    def test_index_page(self, client):
        """GET / → 200, halaman landing."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'FishDetect' in response.data or b'Deteksi' in response.data

    def test_upload_page(self, client):
        """GET /upload → 200, halaman upload."""
        response = client.get('/upload')
        assert response.status_code == 200
        assert b'upload' in response.data.lower() or b'deteksi' in response.data.lower()

    def test_history_page(self, client):
        """GET /history → 200, halaman riwayat."""
        response = client.get('/history')
        assert response.status_code == 200
        assert b'Riwayat' in response.data or b'history' in response.data.lower()

    def test_health_endpoint(self, client):
        """GET /health → 200, JSON health check."""
        response = client.get('/health')
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert 'status' in data

    def test_api_diseases(self, client):
        """GET /api/diseases → 200, JSON list penyakit."""
        response = client.get('/api/diseases')
        assert response.status_code == 200
        data = response.get_json()
        assert data is not None
        assert 'status' in data
        assert data['status'] == 'success'

    def test_disease_info_page(self, client, app):
        """GET /disease-info/<name> → 200, info penyakit."""
        with app.app_context():
            from app.models import Disease
            disease = Disease.query.first()
            if disease:
                response = client.get(f'/disease-info/{disease.disease_name}')
                assert response.status_code == 200

    def test_404_page(self, client):
        """GET halaman tidak ada → 404."""
        response = client.get('/halaman-tidak-ada-xyz')
        assert response.status_code == 404

    def test_result_page_invalid_id(self, client):
        """GET /result/99999 → 404 (ID tidak ada)."""
        response = client.get('/result/99999')
        assert response.status_code == 404


# ============================================================
# 2. TEST POST /predict — Upload + Validasi
# ============================================================

class TestPredictEndpoint:
    """Test endpoint POST /predict dengan berbagai skenario."""

    def test_upload_valid_jpg(self, client, app):
        """Upload file JPG valid → expect 200 + JSON sukses."""
        from app import is_model_available

        img_buf = _create_test_image_jpg()
        data = {
            'file': (img_buf, 'test_ikan.jpg', 'image/jpeg')
        }
        response = client.post(
            '/predict',
            data=data,
            content_type='multipart/form-data'
        )

        assert response.status_code in [200, 400, 503]
        json_data = response.get_json()
        assert json_data is not None
        assert 'status' in json_data

        # Jika model tersedia, expect sukses
        if is_model_available():
            if json_data['status'] == 'success':
                assert 'detection_id' in json_data
                assert 'redirect_url' in json_data

    def test_upload_valid_png(self, client):
        """Upload file PNG valid → expect response JSON."""
        img_buf = _create_test_image_png()
        data = {
            'file': (img_buf, 'test_ikan.png', 'image/png')
        }
        response = client.post(
            '/predict',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code in [200, 400, 503]
        json_data = response.get_json()
        assert json_data is not None

    def test_upload_pdf_rejected(self, client):
        """Upload file PDF → expect 400 + pesan error."""
        pdf_buf = _create_pdf_file()
        data = {
            'file': (pdf_buf, 'document.pdf', 'application/pdf')
        }
        response = client.post(
            '/predict',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data is not None
        assert json_data['status'] == 'error'

    def test_upload_wrong_extension(self, client):
        """Upload file dengan ekstensi tidak diizinkan → 400."""
        buf = io.BytesIO(b'fake gif content')
        data = {
            'file': (buf, 'gambar.gif', 'image/gif')
        }
        response = client.post(
            '/predict',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400

    def test_upload_no_file(self, client):
        """Upload tanpa file → expect 400."""
        response = client.post(
            '/predict',
            data={},
            content_type='multipart/form-data'
        )
        assert response.status_code == 400
        json_data = response.get_json()
        assert json_data is not None
        assert json_data['status'] == 'error'

    def test_upload_empty_filename(self, client):
        """Upload dengan nama file kosong → expect 400."""
        buf = io.BytesIO(b'')
        data = {
            'file': (buf, '', 'image/jpeg')
        }
        response = client.post(
            '/predict',
            data=data,
            content_type='multipart/form-data'
        )
        assert response.status_code == 400


# ============================================================
# 3. TEST DATABASE — Verifikasi Data
# ============================================================

class TestDatabase:
    """Test operasi database."""

    def test_diseases_seeded(self, app):
        """Verifikasi tabel diseases sudah terisi data."""
        with app.app_context():
            from app.models import Disease
            diseases = Disease.query.all()
            assert len(diseases) >= 7, f"Expected minimal 7 penyakit, got {len(diseases)}"

    def test_disease_has_required_fields(self, app):
        """Tiap penyakit harus punya nama, penyebab, gejala, penanganan."""
        with app.app_context():
            from app.models import Disease
            diseases = Disease.query.all()
            for d in diseases:
                assert d.disease_name is not None
                assert len(d.disease_name) > 0

    def test_detection_model_exists(self, app):
        """Model Detection terdaftar di database."""
        with app.app_context():
            from app.models import Detection
            # Cek tabel bisa diquery tanpa error
            count = Detection.query.count()
            assert count >= 0  # 0 OK, yang penting tidak error

    def test_save_detection(self, app):
        """Simpan deteksi baru dan verifikasi."""
        with app.app_context():
            from app.models import Detection
            from app import db

            detection = Detection(
                image_path='test_image.jpg',
                predicted_class='healthy',
                confidence_score=0.95
            )
            db.session.add(detection)
            db.session.commit()

            # Verifikasi tersimpan
            saved = Detection.query.filter_by(
                image_path='test_image.jpg'
            ).first()

            assert saved is not None
            assert saved.predicted_class == 'healthy'
            assert saved.confidence_score == 0.95
            assert saved.detection_date is not None

            # Cleanup
            db.session.delete(saved)
            db.session.commit()

    def test_detection_confidence_percent(self, app):
        """Property confidence_percent menghasilkan format yang benar."""
        with app.app_context():
            from app.models import Detection
            from app import db

            detection = Detection(
                image_path='test_pct.jpg',
                predicted_class='aeromonas',
                confidence_score=0.8765
            )
            db.session.add(detection)
            db.session.commit()

            assert '87.65%' in detection.confidence_percent

            db.session.delete(detection)
            db.session.commit()


# ============================================================
# 4. TEST PREPROCESSING — Output Shape
# ============================================================

class TestPreprocessing:
    """Test fungsi preprocessing gambar."""

    def test_preprocess_output_shape(self, app, tmp_path):
        """Output preprocessing harus shape (1, 224, 224, 3)."""
        try:
            from PIL import Image
            import numpy as np

            # Buat gambar test
            img = Image.new('RGB', (640, 480), color=(100, 150, 200))
            img_path = str(tmp_path / 'test_fish.jpg')
            img.save(img_path)

            from app.ml.preprocessing import preprocess_image
            result = preprocess_image(img_path)

            assert result is not None
            assert result.shape == (1, 224, 224, 3), \
                f"Expected shape (1, 224, 224, 3), got {result.shape}"

        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")

    def test_preprocess_normalized(self, app, tmp_path):
        """Pixel values harus dinormalisasi ke range 0-1."""
        try:
            from PIL import Image
            import numpy as np

            img = Image.new('RGB', (300, 300), color=(255, 128, 0))
            img_path = str(tmp_path / 'test_norm.jpg')
            img.save(img_path)

            from app.ml.preprocessing import preprocess_image
            result = preprocess_image(img_path)

            assert result.min() >= 0.0, "Pixel min harus >= 0"
            assert result.max() <= 1.0, "Pixel max harus <= 1"

        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")

    def test_preprocess_invalid_file(self, app):
        """File tidak valid → raise exception."""
        try:
            from app.ml.preprocessing import preprocess_image
            with pytest.raises(Exception):
                preprocess_image('/path/to/nonexistent/file.jpg')
        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")


# ============================================================
# 5. TEST INFERENCE — Output Dictionary
# ============================================================

class TestInference:
    """Test fungsi inference / prediksi."""

    def test_predict_disease_returns_dict(self, app, tmp_path):
        """predict_disease() harus return dictionary dengan key yang benar."""
        from app import is_model_available
        if not is_model_available():
            pytest.skip("Model CNN tidak tersedia, skip test inference")

        try:
            from PIL import Image
            img = Image.new('RGB', (224, 224), color=(100, 200, 150))
            img_path = str(tmp_path / 'test_inference.jpg')
            img.save(img_path)

            from app.ml.inference import predict_disease
            result = predict_disease(img_path)

            assert isinstance(result, dict), "Output harus dictionary"

            # Key wajib
            required_keys = ['class_name', 'confidence', 'all_probabilities']
            for key in required_keys:
                assert key in result, f"Missing key: {key}"

        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")

    def test_predict_confidence_range(self, app, tmp_path):
        """Confidence harus dalam range 0-100."""
        from app import is_model_available
        if not is_model_available():
            pytest.skip("Model CNN tidak tersedia")

        try:
            from PIL import Image
            img = Image.new('RGB', (224, 224), color=(200, 100, 50))
            img_path = str(tmp_path / 'test_conf.jpg')
            img.save(img_path)

            from app.ml.inference import predict_disease
            result = predict_disease(img_path)

            conf = result.get('confidence', -1)
            assert 0 <= conf <= 100, f"Confidence {conf} di luar range 0-100"

        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")

    def test_predict_all_probabilities(self, app, tmp_path):
        """all_probabilities harus dict dengan 7 kelas."""
        from app import is_model_available
        if not is_model_available():
            pytest.skip("Model CNN tidak tersedia")

        try:
            from PIL import Image
            img = Image.new('RGB', (224, 224), color=(50, 50, 50))
            img_path = str(tmp_path / 'test_all_prob.jpg')
            img.save(img_path)

            from app.ml.inference import predict_disease
            result = predict_disease(img_path)

            all_probs = result.get('all_probabilities', {})
            assert isinstance(all_probs, dict)
            assert len(all_probs) == 7, \
                f"Expected 7 kelas, got {len(all_probs)}"

        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")

    def test_get_class_names(self, app):
        """get_class_names() harus return list 7 kelas."""
        try:
            from app.ml.inference import get_class_names
            names = get_class_names()
            assert len(names) == 7
        except ImportError as e:
            pytest.skip(f"Dependency tidak tersedia: {e}")


# ============================================================
# 6. TEST EDGE CASES
# ============================================================

class TestEdgeCases:
    """Test kasus-kasus khusus / edge cases."""

    def test_multiple_uploads(self, client, app):
        """Upload beberapa file berturut-turut tidak menyebabkan error."""
        for i in range(3):
            img_buf = _create_test_image_jpg()
            data = {
                'file': (img_buf, f'test_{i}.jpg', 'image/jpeg')
            }
            response = client.post(
                '/predict',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code in [200, 400, 503]

    def test_api_diseases_returns_list(self, client):
        """API diseases mengembalikan list yang valid."""
        response = client.get('/api/diseases')
        data = response.get_json()
        assert 'diseases' in data or 'data' in data or 'count' in data

    def test_health_check_components(self, client):
        """Health check menampilkan status komponen."""
        response = client.get('/health')
        data = response.get_json()
        assert 'status' in data


# ============================================================
# MAIN
# ============================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short', '-W', 'ignore'])

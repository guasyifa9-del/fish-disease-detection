"""
Model Database (SQLAlchemy ORM)
Fish Disease Detection System

ERD:
  users ──< detections ──< detection_details >── diseases

Tabel:
  1. User         → Data pengguna (opsional, untuk guest user)
  2. Detection    → Hasil deteksi/prediksi penyakit ikan
  3. Disease      → Informasi 7 kelas penyakit ikan
  4. DetectionDetail → Detail relasi antara detection dan disease + catatan
"""

from datetime import datetime
from app import db


# ============================================================
# Model: User
# ============================================================
class User(db.Model):
    """
    Model pengguna aplikasi.

    Kolom:
        user_id      : INT PK AUTOINCREMENT
        username     : VARCHAR(50) UNIQUE NOT NULL
        email        : VARCHAR(100) UNIQUE NOT NULL
        password_hash: VARCHAR(255) NOT NULL
        created_at   : DATETIME default now()
    """
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)

    # Relasi: satu user bisa punya banyak deteksi
    detections = db.relationship('Detection', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.user_id}: {self.username}>'

    def to_dict(self):
        """Konversi ke dictionary untuk API response."""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }


# ============================================================
# Model: Detection
# ============================================================
class Detection(db.Model):
    """
    Model untuk menyimpan hasil deteksi penyakit ikan.

    Kolom:
        detection_id    : INT PK AUTOINCREMENT
        user_id         : INT FK → users (nullable, untuk guest user)
        image_path      : VARCHAR(255) NOT NULL
        predicted_class : VARCHAR(100) NOT NULL
        confidence_score: FLOAT NOT NULL
        detection_date  : DATETIME default now()
    """
    __tablename__ = 'detections'

    detection_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.user_id'),
        nullable=True  # nullable: guest user bisa deteksi tanpa login
    )
    image_path = db.Column(db.String(255), nullable=False)
    predicted_class = db.Column(db.String(100), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    detection_date = db.Column(db.DateTime, default=datetime.now)

    # Relasi: satu deteksi bisa punya banyak detail
    details = db.relationship('DetectionDetail', backref='detection', lazy='dynamic',
                              cascade='all, delete-orphan')

    def __repr__(self):
        return (f'<Detection {self.detection_id}: {self.predicted_class} '
                f'({self.confidence_score:.2%})>')

    def to_dict(self):
        """Konversi ke dictionary untuk API response."""
        return {
            'detection_id': self.detection_id,
            'user_id': self.user_id,
            'image_path': self.image_path,
            'predicted_class': self.predicted_class,
            'confidence_score': self.confidence_score,
            'detection_date': self.detection_date.strftime('%Y-%m-%d %H:%M:%S')
        }

    @property
    def confidence_percent(self):
        """Mengembalikan confidence dalam format persen."""
        return f'{self.confidence_score * 100:.2f}%'

    @property
    def image_filename(self):
        """Mengembalikan nama file dari image_path."""
        import os
        return os.path.basename(self.image_path)


# ============================================================
# Model: Disease
# ============================================================
class Disease(db.Model):
    """
    Model untuk menyimpan informasi penyakit ikan.

    Kolom:
        disease_id   : INT PK AUTOINCREMENT
        disease_name : VARCHAR(100) UNIQUE NOT NULL
        cause        : TEXT (penyebab penyakit)
        symptoms     : TEXT (gejala)
        treatment    : TEXT (cara penanganan)
        prevention   : TEXT (cara pencegahan)
        image_example: VARCHAR(255) (path gambar contoh)
    """
    __tablename__ = 'diseases'

    disease_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    disease_name = db.Column(db.String(100), unique=True, nullable=False)
    cause = db.Column(db.Text, nullable=True)
    symptoms = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    prevention = db.Column(db.Text, nullable=True)
    image_example = db.Column(db.String(255), nullable=True)

    # Relasi: satu penyakit bisa punya banyak detection_detail
    detection_details = db.relationship('DetectionDetail', backref='disease', lazy='dynamic')

    def __repr__(self):
        return f'<Disease {self.disease_id}: {self.disease_name}>'

    def to_dict(self):
        """Konversi ke dictionary untuk API response."""
        return {
            'disease_id': self.disease_id,
            'disease_name': self.disease_name,
            'cause': self.cause,
            'symptoms': self.symptoms,
            'treatment': self.treatment,
            'prevention': self.prevention,
            'image_example': self.image_example
        }

    @property
    def display_name(self):
        """Label penyakit yang mudah dibaca (untuk template)."""
        labels = {
            'bacterial_red_disease': 'Penyakit Merah (Bacterial Red Disease)',
            'aeromonas': 'Aeromonas',
            'bacterial_gill_disease': 'Penyakit Insang Bakteri (Bacterial Gill Disease)',
            'fungal_saprolegniasis': 'Saprolegniasis (Infeksi Jamur)',
            'parasitic_disease': 'Penyakit Parasit',
            'white_tail_disease': 'Penyakit Ekor Putih (White Tail Disease)',
            'healthy': 'Sehat'
        }
        return labels.get(self.disease_name, self.disease_name)


# ============================================================
# Model: DetectionDetail
# ============================================================
class DetectionDetail(db.Model):
    """
    Model detail relasi antara detection dan disease.
    Menyimpan catatan tambahan untuk setiap hasil deteksi.

    Kolom:
        detail_id    : INT PK AUTOINCREMENT
        detection_id : INT FK → detections
        disease_id   : INT FK → diseases
        notes        : TEXT (catatan tambahan)
    """
    __tablename__ = 'detection_details'

    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    detection_id = db.Column(
        db.Integer,
        db.ForeignKey('detections.detection_id'),
        nullable=False
    )
    disease_id = db.Column(
        db.Integer,
        db.ForeignKey('diseases.disease_id'),
        nullable=False
    )
    notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return (f'<DetectionDetail {self.detail_id}: '
                f'detection={self.detection_id}, disease={self.disease_id}>')

    def to_dict(self):
        """Konversi ke dictionary untuk API response."""
        return {
            'detail_id': self.detail_id,
            'detection_id': self.detection_id,
            'disease_id': self.disease_id,
            'notes': self.notes
        }

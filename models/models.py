from datetime import datetime, date, time
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from models.extensions import db


class Admin(UserMixin, db.Model):
    """Admin / staff login account."""
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="admin")  # admin / staff (role-based access)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)


class Student(db.Model):
    """A registered student/employee whose face is enrolled in the system."""
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(40), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    roll_no = db.Column(db.String(40), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    year = db.Column(db.String(20), nullable=True)
    section = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)   # representative thumbnail
    is_encoded = db.Column(db.Boolean, default=False)        # has a face encoding been generated
    images_captured = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    attendance_records = db.relationship(
        "Attendance", backref="student", lazy="dynamic", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "roll_no": self.roll_no,
            "department": self.department,
            "year": self.year,
            "section": self.section,
            "email": self.email,
            "phone": self.phone,
            "is_encoded": self.is_encoded,
            "images_captured": self.images_captured,
        }


class Attendance(db.Model):
    """One row per student per day (enforces the one-mark-per-day rule)."""
    __tablename__ = "attendance"

    id = db.Column(db.Integer, primary_key=True)
    student_pk = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False, index=True)
    student_id = db.Column(db.String(40), nullable=False)     # denormalised for fast reporting
    name = db.Column(db.String(120), nullable=False)
    roll_no = db.Column(db.String(40), nullable=False)
    department = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    time_in = db.Column(db.Time, default=lambda: datetime.now().time())
    status = db.Column(db.String(20), default="Present")      # Present / Late / Absent
    confidence = db.Column(db.Float, nullable=True)            # recognition confidence %

    __table_args__ = (
        db.UniqueConstraint("student_pk", "date", name="uq_one_mark_per_day"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "roll_no": self.roll_no,
            "department": self.department,
            "date": self.date.isoformat(),
            "time_in": self.time_in.strftime("%H:%M:%S") if self.time_in else None,
            "status": self.status,
            "confidence": self.confidence,
        }


class UnknownFace(db.Model):
    """Snapshot log of faces the system could not match to any student."""
    __tablename__ = "unknown_faces"

    id = db.Column(db.Integer, primary_key=True)
    snapshot_path = db.Column(db.String(255), nullable=False)
    detected_at = db.Column(db.DateTime, default=datetime.utcnow)
    reviewed = db.Column(db.Boolean, default=False)


class SystemSetting(db.Model):
    """
    Single-row table holding runtime-tunable settings (camera index, thresholds, etc.)
    so admins can adjust them from the UI without editing config.py and restarting.
    Falls back to config.py defaults if no row exists yet.
    """
    __tablename__ = "system_settings"

    id = db.Column(db.Integer, primary_key=True)
    camera_index = db.Column(db.Integer, default=0)
    frame_skip = db.Column(db.Integer, default=2)
    frame_resize_scale = db.Column(db.Float, default=0.5)
    face_match_tolerance = db.Column(db.Float, default=0.45)
    min_confidence_to_mark = db.Column(db.Integer, default=55)
    liveness_enabled = db.Column(db.Boolean, default=True)
    ear_blink_threshold = db.Column(db.Float, default=0.21)
    late_after_time = db.Column(db.String(5), default="09:15")
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def current(cls):
        row = cls.query.first()
        if row is None:
            row = cls()
            db.session.add(row)
            db.session.commit()
        return row


class SystemLog(db.Model):
    """Unified log table for login / recognition / attendance / error events."""
    __tablename__ = "system_logs"

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(30), nullable=False)  # login | recognition | attendance | error | system
    message = db.Column(db.Text, nullable=False)
    actor = db.Column(db.String(80), nullable=True)       # admin username or "system"
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            "id": self.id,
            "category": self.category,
            "message": self.message,
            "actor": self.actor,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

"""
Central configuration for the Face Recognition Attendance System.
All tunables live here so behaviour can be changed without touching app logic.
"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # --- Core / security -----------------------------------------------
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'database', 'attendance.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)

    WTF_CSRF_ENABLED = True

    # --- Folder layout ----------------------------------------------------
    DATASET_DIR = os.path.join(BASE_DIR, "dataset")          # raw face crops per student
    ENCODINGS_DIR = os.path.join(BASE_DIR, "encodings")
    ENCODINGS_FILE = os.path.join(ENCODINGS_DIR, "encodings.pkl")
    ATTENDANCE_EXPORT_DIR = os.path.join(BASE_DIR, "attendance")
    UNKNOWN_FACES_DIR = os.path.join(BASE_DIR, "uploads", "unknown_faces")
    LOG_DIR = os.path.join(BASE_DIR, "logs")

    # --- Face recognition tuning -------------------------------------------
    IMAGES_PER_STUDENT = 30           # how many frames to capture during registration
    MIN_IMAGES_PER_STUDENT = 15       # below this, refuse to encode (low quality dataset)
    FACE_DETECTION_MODEL = "hog"      # "hog" (CPU, fast) or "cnn" (GPU, slower/more accurate)
    FACE_MATCH_TOLERANCE = 0.45       # lower = stricter match (euclidean distance threshold)
    FRAME_RESIZE_SCALE = 0.5          # downscale factor applied before detection, for speed
    FRAME_SKIP = 2                    # only run detection on every Nth frame
    MIN_CONFIDENCE_TO_MARK = 55       # % confidence required to auto-mark attendance

    # --- Anti-spoofing (basic liveness) ------------------------------------
    LIVENESS_ENABLED = True
    EAR_BLINK_THRESHOLD = 0.21        # eye-aspect-ratio below this = eye considered closed
    LIVENESS_REQUIRED_BLINKS = 1      # blinks required within the verification window
    LIVENESS_WINDOW_SECONDS = 6       # time window to detect a blink before flagging "no liveness"

    # --- Attendance rules ---------------------------------------------------
    ONE_MARK_PER_DAY = True
    OFFICE_START_TIME = "09:00"
    LATE_AFTER_TIME = "09:15"

    # --- Misc -----------------------------------------------------------------
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload cap


def ensure_directories():
    """Create all required folders on first run."""
    for path in [
        Config.DATASET_DIR,
        Config.ENCODINGS_DIR,
        Config.ATTENDANCE_EXPORT_DIR,
        Config.UNKNOWN_FACES_DIR,
        Config.LOG_DIR,
        os.path.join(BASE_DIR, "database"),
    ]:
        os.makedirs(path, exist_ok=True)

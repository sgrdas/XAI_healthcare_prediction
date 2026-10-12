"""
config.py - Application Configuration Module
=============================================
Defines configuration classes for different environments:
- DevelopmentConfig: Local development with SQLite (zero-setup)
- TestingConfig: Isolated testing environment (in-memory SQLite)
- ProductionConfig: Hardened production settings (MySQL)

All secrets are read from environment variables for security.
"""

import os
from datetime import timedelta
from dotenv import load_dotenv

from urllib.parse import quote_plus

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load environment variables from .env file explicitly
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)
load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"), override=True)


def build_database_uri(db_type: str = None) -> str:
    """
    Construct database URI based on environment variables.
    Supports MySQL, SQLite, or direct SQLALCHEMY_DATABASE_URI / DATABASE_URL.
    """
    explicit_uri = os.environ.get("DATABASE_URL") or os.environ.get("SQLALCHEMY_DATABASE_URI")
    if explicit_uri:
        return explicit_uri

    selected_type = (db_type or os.environ.get("DB_TYPE", "mysql")).lower().strip()

    if selected_type == "sqlite":
        db_path = os.path.join(BASE_DIR, "database", "healthai.db")
        return f"sqlite:///{db_path}"

    # Default to MySQL / MariaDB (e.g. XAMPP or standalone)
    user = os.environ.get("DB_USER", "root")
    pwd  = os.environ.get("DB_PASSWORD", "")
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "3306")
    name = os.environ.get("DB_NAME", "explainable_ai_health")

    encoded_pwd = quote_plus(pwd) if pwd else ""
    auth = f"{user}:{encoded_pwd}" if encoded_pwd else user
    return f"mysql+pymysql://{auth}@{host}:{port}/{name}?charset=utf8mb4"


class BaseConfig:
    """Base configuration shared across all environments."""

    # ── Flask ──────────────────────────────────────────────────────────────
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production-secret-key-123!")
    DEBUG = False
    TESTING = False

    # ── Database ───────────────────────────────────────────────────────
    DB_TYPE     = os.environ.get("DB_TYPE", "mysql")
    DB_USER     = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST     = os.environ.get("DB_HOST", "localhost")
    DB_PORT     = os.environ.get("DB_PORT", "3306")
    DB_NAME     = os.environ.get("DB_NAME", "explainable_ai_health")

    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # ── Session ────────────────────────────────────────────────────────────
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # ── CSRF ───────────────────────────────────────────────────────────────
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hour

    # ── Mail ───────────────────────────────────────────────────────────────
    MAIL_SERVER   = os.environ.get("MAIL_SERVER", "smtp.gmail.com").strip()
    MAIL_PORT     = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS  = os.environ.get("MAIL_USE_TLS", "true").lower() in ("true", "1")
    MAIL_USE_SSL  = os.environ.get("MAIL_USE_SSL", "false").lower() in ("true", "1")
    _raw_mail_user = os.environ.get("MAIL_USERNAME", "").strip()
    MAIL_USERNAME = _raw_mail_user
    _raw_mail_pass = os.environ.get("MAIL_PASSWORD", "").strip()
    MAIL_PASSWORD = _raw_mail_pass.replace(" ", "") if len(_raw_mail_pass.replace(" ", "")) == 16 else _raw_mail_pass
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER") or (f"Explainable AI Health <{_raw_mail_user}>" if _raw_mail_user and "@" in _raw_mail_user else "Explainable AI Health <noreply@healthai.com>")

    # ── Google OAuth 2.0 ───────────────────────────────────────────────────
    GOOGLE_CLIENT_ID     = os.environ.get("GOOGLE_CLIENT_ID") or "1084293847291-healthaidemo73829104example.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET") or "GOCSPX-demoHealthAiOAuthSecretKey2026Example"

    # ── File Uploads ───────────────────────────────────────────────────────
    UPLOAD_FOLDER   = os.path.join(BASE_DIR, "uploads")
    DATASET_FOLDER  = os.path.join(BASE_DIR, "datasets")
    REPORTS_FOLDER  = os.path.join(BASE_DIR, "reports")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload
    ALLOWED_EXTENSIONS = {"csv", "xlsx", "xls"}

    # ── ML Models ──────────────────────────────────────────────────────────
    MODELS_FOLDER = os.path.join(BASE_DIR, "ml", "saved_models")

    # ── Pagination ─────────────────────────────────────────────────────────
    PREDICTIONS_PER_PAGE = 10
    USERS_PER_PAGE       = 20

    # ── Token Expiry (Email verification / Password reset) ─────────────────
    EMAIL_TOKEN_EXPIRY         = 3600       # 1 hour
    PASSWORD_RESET_EXPIRY      = 1800       # 30 minutes

    # ── Bcrypt ─────────────────────────────────────────────────────────────
    BCRYPT_LOG_ROUNDS = 12


class DevelopmentConfig(BaseConfig):
    """Development configuration supporting MySQL or SQLite."""

    DEBUG = True
    SQLALCHEMY_ECHO = False        # set True to log SQL queries
    SESSION_COOKIE_SECURE = False  # allow HTTP in dev
    SQLALCHEMY_DATABASE_URI = build_database_uri()


class TestingConfig(BaseConfig):
    """Testing configuration using an in-memory SQLite database."""

    TESTING = True
    WTF_CSRF_ENABLED = False       # disable CSRF for test client
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    BCRYPT_LOG_ROUNDS = 4          # speed up tests


class ProductionConfig(BaseConfig):
    """Production configuration with MySQL and security hardened."""

    SESSION_COOKIE_SECURE = True   # HTTPS only
    SESSION_COOKIE_HTTPONLY = True
    PREFERRED_URL_SCHEME = "https"
    SQLALCHEMY_DATABASE_URI = build_database_uri("mysql")
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    }


# ── Config registry ────────────────────────────────────────────────────────
config_map = {
    "development": DevelopmentConfig,
    "testing":     TestingConfig,
    "production":  ProductionConfig,
    "default":     DevelopmentConfig,
}


def get_config(env: str = None) -> BaseConfig:
    """
    Return the configuration class for the given environment name.

    Args:
        env: One of 'development', 'testing', 'production'.
             Falls back to FLASK_ENV env-var, then 'default'.

    Returns:
        Configuration class (not an instance).
    """
    env = env or os.environ.get("FLASK_ENV", "default")
    return config_map.get(env, DevelopmentConfig)

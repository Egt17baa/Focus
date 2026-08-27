import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("FOCUS_SECRET_KEY", "dev-secret-change-me-please-32-bytes")
    JWT_SECRET_KEY = os.environ.get("FOCUS_JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.environ.get("FOCUS_ACCESS_TOKEN_MINUTES", "60"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.environ.get("FOCUS_REFRESH_TOKEN_DAYS", "30"))
    )
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "FOCUS_DATABASE_URI", "sqlite:///" + os.path.join(os.getcwd(), "focus.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.environ.get("FOCUS_CORS_ORIGINS", "*")
    JSON_SORT_KEYS = False


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-secret-key-for-unit-tests-only"

import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    # Данные для PostgreSQL
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB")

    # Данные бота
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    BOT_API_SECRET_KEY = os.getenv("BOT_API_SECRET_KEY")

    # Настройки MinIO
    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET")
    __MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower()
    if __MINIO_SECURE == "true":
        MINIO_SECURE = True
    elif __MINIO_SECURE == "false":
        MINIO_SECURE = False
    else:
        raise ValueError("Incorrect value for MINIO_SECURE")

    # Домен фронтенда
    FRONTEND_ORIGIN = os.getenv(
        "FRONTEND_ORIGIN",
        "http://localhost:3000",
    )

    # Настройки JWT
    JWT_SECRET_KEY= os.getenv("JWT_SECRET_KEY")
    JWT_ALGORITHM= os.getenv("JWT_ALGORITHM")
    JWT_LIFE_LENGTH= int(os.getenv("JWT_LIFE_LENGTH"))

    # URL FastAPI для внутренних запросов из контейнера бота
    BACKEND_INTERNAL_URL = os.getenv(
        "BACKEND_INTERNAL_URL",
        "http://127.0.0.1:8000",
    )

    # Конфигурация бота
    BOT_MODE = os.getenv("BOT_MODE", "polling").lower()

    # Общее хранилище состояний между экземплярами
    REDIS_URL = os.getenv(
        "REDIS_URL",
        "redis://localhost:6379/0",
    )

    # Настройки webhook для production
    BOT_WEBHOOK_URL = os.getenv("BOT_WEBHOOK_URL")
    BOT_WEBHOOK_PATH = os.getenv(
        "BOT_WEBHOOK_PATH",
        "/telegram/webhook",
    )
    BOT_WEBHOOK_SECRET = os.getenv("BOT_WEBHOOK_SECRET")

    BOT_WEBHOOK_HOST = os.getenv(
        "BOT_WEBHOOK_HOST",
        "0.0.0.0",
    )
    BOT_WEBHOOK_PORT = int(
        os.getenv("BOT_WEBHOOK_PORT", "8080")
    )

    # Назначение и проверка команды администратора
    ADMIN_COMMAND = os.getenv("ADMIN_COMMAND", "").strip().lower() or None

    ADMIN_BOOTSTRAP_ENABLED = (
            os.getenv("ADMIN_BOOTSTRAP_ENABLED", "false").strip().lower()
            == "true"
    )

settings = Settings()

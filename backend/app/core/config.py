from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    GEMINI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[3] / ".env")

settings = Settings()    
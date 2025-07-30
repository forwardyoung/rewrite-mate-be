# app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # .env 파일의 모든 변수를 여기에 명시
    ANTHROPIC_API_KEY: Optional[str] = None
    DEBUG: bool = False
    PROJECT_NAME: str = "English Rewrite Tutor"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"


settings = Settings()
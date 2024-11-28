from sqlmodel import create_engine, SQLModel, Session
from pydantic_settings import BaseSettings
from pydantic import Field, EmailStr
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None

    # Email settings
    smtp_server: str = Field(env="SMTP_SERVER")
    smtp_port: int = Field(env="SMTP_PORT")
    smtp_user: EmailStr = Field(env="SMTP_USER")
    smtp_password: str = Field(env="SMTP_PASSWORD")
    database_url: str = Field(env="DATABASE_URL")
    secret_key: str = Field(env="SECRET_KEY")

    class Config:
        env_file = ".env"  # .env 파일 자동 로드

# Pydantic Settings 인스턴스 생성
settings = Settings()

# SQLModel 엔진 설정
engine_url = create_engine(settings.DATABASE_URL, echo=True)

def conn():
    SQLModel.metadata.create_all(engine_url)

def get_session():
    with Session(engine_url) as session:
        yield session


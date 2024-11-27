from sqlmodel import create_engine, SQLModel, Session
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: Optional[str] = None
    SECRET_KEY: Optional[str] = None

    class Config:
        env_file = ".env"


settings = Settings()
engine_url = create_engine(settings.DATABASE_URL, echo=True)


def conn():
    SQLModel.metadata.create_all(engine_url)


def get_session():
    with Session(engine_url) as session:
        yield session

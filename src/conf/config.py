from typing import Any

from pydantic import ConfigDict, field_validator, EmailStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings) :
    DB_URL: str = "postgresql+asyncpg://DB_USERNAME:DB_PASSWORD@BD_HOST:5432/DB_NAME"
    SECRET_KEY_JWT: str = "1234567890"
    ALGORITHM: str = "HS256"
    MAIL_USERNAME: EmailStr = "postgres@gmail.com"
    MAIL_PASSWORD: str = "1234567890"
    MAIL_FROM: str = "postgres@gmail.com"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.gmail.com"
    REDIS_DOMAIN: str = 'localhost'
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    CLD_NAME: str = 'SKY'
    CLD_API_KEY: int = 1234567890
    CLD_API_SECRET: str = "secret"

    @field_validator("ALGORITHM")
    @classmethod
    def validate_algorithm(cls, v: Any) :
        if v not in ["HS256", "HS512"] :
            raise ValueError("algorithm must be HS256 or HS512")
        return v

    model_config = ConfigDict(extra = 'ignore', env_file = ".env", env_file_encoding = "utf-8")  


config = Settings()

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from enum import Enum

class DatabaseType(str, Enum):
    POSTGRES = "postgres"
    DYNAMODB = "dynamodb"

class Settings(BaseSettings):
    DATABASE_TYPE: DatabaseType = DatabaseType.POSTGRES # Default to postgres

    # --------------------------------------------------------------------
    # Postgres settings
    POSTGRES_DATABASE_URL: str = "postgresql+asyncpg://user:password@postgresql:5432/crypto_db"
    POSTGRES_DATABASE_URL_FOR_TESTING: str = "postgresql+asyncpg://postgres:password@postgresql:5432/crypto_db"
    
    # Debezium settings (only related to postgres)
    DB_HOST: str = "postgresql"
    DB_PORT: str = "5432"
    DB_USER: str = "user_service_user"
    DB_PASSWORD: str = "super_secure_password"
    DB_NAME: str = "crypto_db"
    DEBEZIUM_URL: str = "http://debezium:8083/connectors"
    # --------------------------------------------------------------------

    # --------------------------------------------------------------------
    # AWS settings
    AWS_ACCESS_KEY_ID: str = "default_key"
    AWS_SECRET_ACCESS_KEY: str = "default_secret"
    AWS_REGION: str = "us-east-1"
    AWS_ENDPOINT: str = "http://localhost:4566"

    AWS_ACCESS_KEY_ID_FOR_TESTING: str = "default_key"
    AWS_SECRET_ACCESS_KEY_FOR_TESTING: str = "default_secret"
    AWS_REGION_FOR_TESTING: str = "us-east-1"
    AWS_ENDPOINT_FOR_TESTING: str = "http://localstack:4566"
    
    model_config = SettingsConfigDict(
        env_file = ".env",
        case_sensitive = True
    )
    # --------------------------------------------------------------------


@lru_cache()
def get_settings() -> Settings:
    return Settings()

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict  # type: ignore
from pydantic import model_validator


class Settings(BaseSettings):
    """
    Application settings for OverAchiever.
    It can either take a full DATABASE_URL or build one from individual parts.
    """
    # 1. Database Components (Optional if DATABASE_URL is provided)
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    
    # The final string we will use
    DATABASE_URL: str
    
    # 2. Redis & Kafka
    REDIS_URL: str = "redis://redis:6379/0"
    KAFKA_BOOTSTRAP_SERVERS: str = "kafka:29092"
    
    # 3. External API Keys
    STEAM_API_KEY: str = ""
    
    # 4. Project Identity
    PROJECT_NAME: str = "OverAchiever"
    VERSION: str = "0.1.0"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @model_validator(mode="after")
    def assemble_database_url(self) -> "Settings":
        """
        If DATABASE_URL is not provided, we build it from the pieces.
        Formula: postgresql://user:pass@host:port/dbname
        """
        if not self.DATABASE_URL:
            if all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_DB]):
                self.DATABASE_URL = (
                    f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
                    f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
                )
            else:
                # If we still don't have enough info, Pydantic will notice 
                # when we try to use the empty string later.
                pass
        return self

    @property
    def async_database_url(self) -> str:
        """
        Helper to convert postgresql:// to postgresql+asyncpg://
        """
        if self.DATABASE_URL and self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.DATABASE_URL or ""


settings = Settings()

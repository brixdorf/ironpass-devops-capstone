from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings come from environment variables. Nothing secret lives in the code."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # export DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname
    database_url: str = "postgresql+psycopg://ironpass:ironpass@localhost:5432/ironpass"
    # members whose plan ends within this many days count as "expiring soon"
    expiring_soon_days: int = 7


settings = Settings()

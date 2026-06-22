"""Application configuration via pydantic-settings (12-factor / env-driven)."""
from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "postgresql+psycopg://soc:soc@db:5432/soc_maturity"

    # Auth
    secret_key: str = "dev-insecure-secret-change-me"
    access_token_expire_minutes: int = 480
    algorithm: str = "HS256"

    # Seed admin
    admin_username: str = "admin"
    admin_password: str = "admin"
    admin_full_name: str = "Administrador"

    # Ingestion
    frameworks_dir: str = "/frameworks"
    seed_workbook: str = "Viaconnect_HealthCheck_Dominios_SOC_COMPLETOv2.xlsx"
    auto_seed: bool = True


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

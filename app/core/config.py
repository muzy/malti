from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Database settings
    database_url: str = "postgresql://malti_user:malti_password@localhost:5432/malti"

    # Configuration file path
    malti_config_path: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "malti.toml")

    # API settings
    api_v1_prefix: str = "/api/v1"

    # Logging settings
    log_level: str = "INFO"
    sqlalchemy_echo: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
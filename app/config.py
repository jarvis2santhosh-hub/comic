
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root:
# ComicCraft/
# ├── app/
# │   └── config.py
# └── .env
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    environment: str = "development"
    debug: bool = True

    host: str = "127.0.0.1"
    port: int = 8000

    # Gemini
    gemini_api_key: str = ""
    gemini_outline_model: str = "gemini-3.8-flash"
    gemini_story_model: str = "gemini-3.8-flash"

    # Hugging Face
    hf_token: str = ""
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"
    hf_provider: str = "auto"

    # Image generation
    image_backend: str = "huggingface"
    local_diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    local_device: str = "auto"

    # Comic settings
    max_panels: int = 5
    image_width: int = 768
    image_height: int = 1024

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / "app" / "static"

    @property
    def panels_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def exports_dir(self) -> Path:
        return self.static_dir / "exports"

    @property
    def storage_dir(self) -> Path:
        return BASE_DIR / "app" / "storage"


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.panels_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.exports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    settings.storage_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    return settings


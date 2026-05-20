from pathlib import Path
from typing import List

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    app_name: str = "RivalScope"
    studio_name: str = "NeiroBridge"

    proxy_api_key: str = ""
    proxy_api_base_url: str = "https://api.proxyapi.ru/openai/v1"
    openai_model: str = "gpt-4o-mini"
    openai_vision_model: str = "gpt-4o"
    openai_report_model: str = "gpt-4o"

    gigachat_api_key: str = ""
    gigachat_base_url: str = "https://gigachat.devices.sberbank.ru/api/v1"
    enable_gigachat_fallback: bool = False

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    history_limit: int = 30
    max_image_mb: int = 10
    selenium_headless: bool = True
    parser_timeout_seconds: int = 25

    default_competitor_urls: List[str] = [
        "https://neirobridge.ru",
        "https://aiworkflows.ru",
        "https://www.4gic.com",
        "https://cortex-lab.ru",
    ]

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

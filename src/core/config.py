import os
from pydantic import BaseModel
from dotenv import load_dotenv
from .errors import ConfigError

load_dotenv()

class Settings(BaseModel):
    telegram_bot_token: str
    nomi_api_key: str
    nomi_default_nomi_uuid: str | None = None
    log_level: str = "INFO"
    request_timeout_sec: float = 30.0
    rate_limit_rps: float = 0.4
    db_path: str = "./data/app.db"

def get_settings() -> Settings:
    s = Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        nomi_api_key=os.getenv("NOMI_API_KEY", ""),
        nomi_default_nomi_uuid=os.getenv("NOMI_DEFAULT_NOMI_UUID") or None,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        request_timeout_sec=float(os.getenv("REQUEST_TIMEOUT_SEC", "30")),
        rate_limit_rps=float(os.getenv("RATE_LIMIT_RPS", "0.4")),
        db_path=os.getenv("DB_PATH", "./data/app.db"),
    )
    if not s.telegram_bot_token:
        raise ConfigError("TELEGRAM_BOT_TOKEN is missing")
    if not s.nomi_api_key:
        raise ConfigError("NOMI_API_KEY is missing")
    return s

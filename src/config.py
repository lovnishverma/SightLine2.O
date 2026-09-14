import os
from dataclasses import dataclass
from typing import Dict

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class Config:
    """Central configuration for SightLine."""

    # Timing
    CAPTURE_INTERVAL: float = float(os.getenv("SIGHTLINE_CAPTURE_INTERVAL", "3.0"))
    SCENE_THRESHOLD: float = float(os.getenv("SIGHTLINE_SCENE_THRESHOLD", "0.10"))
    DEBOUNCE_MS: int = int(os.getenv("SIGHTLINE_DEBOUNCE_MS", "800"))
    MAX_DIM: int = int(os.getenv("SIGHTLINE_MAX_DIM", "768"))
    HASH_SIZE: int = int(os.getenv("SIGHTLINE_HASH_SIZE", "16"))

    # Audio
    TTS_TIMEOUT: float = float(os.getenv("SIGHTLINE_TTS_TIMEOUT", "12.0"))
    TTS_RATE: str = os.getenv("SIGHTLINE_TTS_RATE", "+8%")
    AUDIO_FORMAT: str = os.getenv("SIGHTLINE_AUDIO_FORMAT", "mp3")
    MAX_QUEUE_SIZE: int = int(os.getenv("SIGHTLINE_MAX_QUEUE_SIZE", "3"))

    # Model
    MODEL_NAME: str = os.getenv("SIGHTLINE_MODEL_NAME", "microsoft/Florence-2-large-ft")
    
    # Text generation limits for tasks
    MAX_NEW_TOKENS: Dict[str, int] = None

    # UI
    APP_NAME: str = "SightLine Intelligence"
    APP_VERSION: str = "2.0-Bharat"

    # iNSIGHTS Configuration
    INSIGHTS_ENABLED: bool = os.getenv("INSIGHTS_ENABLED", "true").lower() in ("true", "1", "yes")
    INSIGHTS_PROVIDER: str = os.getenv("INSIGHTS_PROVIDER", "live")  # "live" or "mock"
    INSIGHTS_API_KEY: str = os.getenv("INSIGHTS_API_KEY", "")
    INSIGHTS_APP_ID: str = os.getenv("INSIGHTS_APP_ID", "6960af55d740f6d891a60e24")
    INSIGHTS_ENDPOINT: str = os.getenv(
        "INSIGHTS_ENDPOINT",
        "https://insights-ai.info/api/apps/6960af55d740f6d891a60e24/integration-endpoints/Core/InvokeLLM"
    )
    INSIGHTS_TIMEOUT: float = float(os.getenv("INSIGHTS_TIMEOUT", "15.0"))
    INSIGHTS_CACHE_TTL: int = int(os.getenv("INSIGHTS_CACHE_TTL", "1800"))
    INSIGHTS_MAX_SOURCES: int = int(os.getenv("INSIGHTS_MAX_SOURCES", "5"))
    INSIGHTS_MODEL: str = os.getenv("INSIGHTS_MODEL", "gemini_3_flash")
    
    def __post_init__(self):
        if self.MAX_NEW_TOKENS is None:
            self.MAX_NEW_TOKENS = {
                "<CAPTION>": 64,
                "<DETAILED_CAPTION>": 120,
                "<MORE_DETAILED_CAPTION>": 200,
                "<OD>": 256,
                "<OCR>": 300,
            }

CONFIG = Config()


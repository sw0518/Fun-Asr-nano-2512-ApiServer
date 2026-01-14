from pydantic_settings import BaseSettings
from typing import Optional, Dict

class Settings(BaseSettings):
    PROJECT_NAME: str = "FunASR Nano API"
    # MODELS configuration: a dictionary mapping model names to their paths
    # Can be set via env var MODELS='{"model1": "/path/1", "model2": "/path/2"}'
    MODELS: Dict[str, str] = {
        "fun-asr-nano-2512": "/media/saixunda/DataDisk/xiaozhi-server/funasr_models/Fun-ASR-MLT-Nano-2512"
    }
    DEVICE: str = "cuda:0" # or "cpu"
    MAX_CONCURRENT_REQUESTS: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()

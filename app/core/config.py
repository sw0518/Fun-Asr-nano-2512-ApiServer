from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "FunASR Nano API"
    MODEL_DIR: str = "FunAudioLLM/Fun-ASR-Nano-2512"
    DEVICE: str = "cuda:0" # or "cpu"
    MAX_CONCURRENT_REQUESTS: int = 10
    
    class Config:
        env_file = ".env"

settings = Settings()

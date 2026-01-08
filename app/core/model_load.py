import os
import torch
from funasr import AutoModel
from funasr.models.fun_asr_nano.model import FunASRNano
from app.core.config import settings
import asyncio
from concurrent.futures import ThreadPoolExecutor
CORE_DIR = os.path.dirname(os.path.abspath(__file__))
print(f"CORE_DIR===={CORE_DIR}")

class ModelManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelManager, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_REQUESTS)
        return cls._instance

    def load_model(self):
        print(f"Loading model from {settings.MODEL_DIR}...")
        # Check if local path exists, otherwise let funasr download
        model_path = settings.MODEL_DIR
        
        self.model = AutoModel(
            model=model_path,
            trust_remote_code=True,
            disable_update=True,
            device=settings.DEVICE,
            remote_code=f"{CORE_DIR}/model.py",
            batch_size=8,
            # vad_model="fsmn-vad", # Optional: enable VAD if needed
            # vad_kwargs={"max_single_segment_time": 30000},
        )

        print("Model loaded successfully.")

    async def transcribe(self, audio_path: str, language: str = "auto"):
        if not self.model:
            raise RuntimeError("Model not initialized")
        
        loop = asyncio.get_event_loop()
        # Run inference in thread pool to avoid blocking the event loop
        result = await loop.run_in_executor(
            self.executor,
            self._inference,
            audio_path,
            language
        )
        return result

    def _inference(self, audio_path: str, language: str):
        # funasr generate API
        # res = model.generate(input=[wav_path], cache={}, batch_size=1, hotwords=[], language=language)
        kwargs = {}
        if language != "auto":
            kwargs["language"] = language
            
        res = self.model.generate(
            input=[audio_path],
            cache={},
            batch_size=1,
            **kwargs
        )
        # res is a list of results
        if res and len(res) > 0:
            return res[0]["text"]
        return ""

    async def transcribe_stream(self, audio_chunk: bytes, cache: dict, is_final: bool = False):
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._inference_stream,
            audio_chunk,
            cache,
            is_final
        )
        return result

    def _inference_stream(self, audio_chunk: bytes, cache: dict, is_final: bool):
        # Note: input expects a list
        # For bytes input, we might need to wrap it or ensure it's in the right format.
        # FunASR often expects PCM or Wav bytes.
        
        # Speculative streaming call
        res = self.model.generate(
            input=[audio_chunk],
            cache=cache,
            is_final=is_final,
            batch_size=1
        )
        if res and len(res) > 0:
            return res[0] # Usually returns a dict with 'text'
        return {}

model_manager = ModelManager()

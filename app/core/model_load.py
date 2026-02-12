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
            cls._instance.models = {}
            cls._instance.executor = ThreadPoolExecutor(max_workers=settings.MAX_CONCURRENT_REQUESTS)
        return cls._instance

    def load_model(self):
        print(f"Loading models from configuration...")
        
        if not settings.MODELS:
            print("Warning: No models configured in settings.MODELS")
            return

        for name, path in settings.MODELS.items():
            print(f"Loading model '{name}' from {path}...")
            try:
                # Use strict path checking if needed, but AutoModel handles remote/local
                model_instance = AutoModel(
                    model=path,
                    trust_remote_code=True,
                    disable_update=True,
                    device=settings.DEVICE,
                    remote_code=f"{CORE_DIR}/model.py",
                    batch_size=8,
                    vad_model="fsmn-vad",
                    vad_kwargs={"max_single_segment_time": 30000},
                )
                self.models[name] = model_instance
                print(f"Model '{name}' loaded successfully.")
            except Exception as e:
                print(f"Failed to load model '{name}': {e}")
        
        if not self.models:
            print("Error: No models were successfully loaded.")

    def get_model(self, model_name: str = None):
        if not self.models:
             raise RuntimeError("No models initialized")
        
        if not model_name:
            # Return the first available model if none specified
            # This serves as a default behavior
            return next(iter(self.models.values()))
        
        if model_name not in self.models:
             # Try to find a default fallback if the specific name isn't found?
             # Or just error out. 
             # If user passes "default" and we have models, maybe map to first?
             if model_name == "default":
                 return next(iter(self.models.values()))
                 
             raise ValueError(f"Model '{model_name}' not found. Available models: {list(self.models.keys())}")
             
        return self.models[model_name]

    async def transcribe(self, audio_path: str, language: str = "auto", model_name: str = None):
        try:
            model = self.get_model(model_name)
        except ValueError as e:
            raise RuntimeError(str(e))

        loop = asyncio.get_event_loop()
        # Run inference in thread pool to avoid blocking the event loop
        result = await loop.run_in_executor(
            self.executor,
            self._inference,
            model,
            audio_path,
            language
        )
        return result

    def _inference(self, model, audio_path: str, language: str):
        # funasr generate API
        kwargs = {}
        if language != "auto":
            kwargs["language"] = language
            
        res = model.generate(
            input=[audio_path],
            cache={},
            batch_size=1,
            **kwargs
        )
        # res is a list of results
        if res and len(res) > 0:
            return res[0]["text"]
        return ""

    async def transcribe_stream(self, audio_chunk: bytes, cache: dict, is_final: bool = False, model_name: str = None):
        try:
            model = self.get_model(model_name)
        except ValueError as e:
            # In streaming, throwing exception might close connection.
            # We'll let the caller handle it or it propagates.
            raise RuntimeError(str(e))

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._inference_stream,
            model,
            audio_chunk,
            cache,
            is_final
        )
        return result

    def _inference_stream(self, model, audio_chunk: bytes, cache: dict, is_final: bool):
        # Speculative streaming call
        res = model.generate(
            input=[audio_chunk],
            cache=cache,
            is_final=is_final,
            batch_size=1
        )
        if res and len(res) > 0:
            return res[0] # Usually returns a dict with 'text'
        return {}

model_manager = ModelManager()

# FunASR Nano API Service

This project provides an OpenAI-compatible Speech-to-Text API and a WebSocket streaming interface using the `Fun-ASR-Nano-2512` model.

## Features

- **OpenAI Compatible API**: `/v1/audio/transcriptions`
- **WebSocket Streaming**: `/v1/audio/stream`
- **Concurrency**: Supports concurrent requests using ThreadPoolExecutor.
- **Docker Deployment**: Ready for deployment on Ubuntu with GPU support.

## Prerequisites

- Docker & Docker Compose
- NVIDIA GPU with drivers installed (nvidia-container-toolkit)
- Model weights downloaded separately

## Setup

1.  **Download Model Weights**:
    Download the `Fun-ASR-Nano-2512` model from ModelScope or HuggingFace to a directory on your host machine (e.g., `./models/Fun-ASR-Nano-2512`).

    ```bash
    # Example using git lfs
    git lfs install
    git clone https://www.modelscope.cn/FunAudioLLM/Fun-ASR-Nano-2512.git models/Fun-ASR-Nano-2512
    ```

2.  **Configure Environment**:
    The `docker-compose.yml` maps `./models` on host to `/models` in container.
    Use `MODELS` environment variable to configure multiple models (JSON format):
    ```bash
    MODELS='{"fun-asr-nano-2512": "/models/Fun-ASR-Nano-2512"}'
    ```

## Deployment

Run the service using Docker Compose:

```bash
docker-compose up -d --build
```

The service will be available at `http://localhost:8000`.

## API Usage

### REST API (OpenAI Style)

```bash
curl http://localhost:8000/v1/audio/transcriptions \
  -F file=@/path/to/audio.wav \
  -F model="fun-asr-nano-2512"
```

### WebSocket Streaming

Connect to `ws://localhost:8000/v1/audio/stream`.
- Send audio bytes (raw PCM or WAV chunks).
- Receive JSON: `{"text": "partial text", "is_final": false}`.
- Send "EOS" text message to finish.

## Testing

Use the provided test script:

```bash
# Install test dependencies
pip install requests websockets

# Test REST API
python test_api.py --file path/to/audio.wav --mode rest

# Test WebSocket API
python test_api.py --file path/to/audio.wav --mode ws
```

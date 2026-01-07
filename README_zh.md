# FunASR Nano 语音识别服务（中文文档）

本项目提供基于 FunASR 的语音识别 API 服务，支持：
- OpenAI 风格的语音识别 REST 接口：`/v1/audio/transcriptions`
- WebSocket 流式语音识别接口：`/v1/audio/stream`
- 并发能力：通过线程池安全地处理多并发请求
- Docker Compose 部署（Ubuntu 服务器，支持 GPU），模型权重通过宿主机目录映射

## 项目结构
- 应用入口：[main.py](file:///d:/fun-asr-nano-api/app/main.py)
- 配置管理：[config.py](file:///d:/fun-asr-nano-api/app/core/config.py)
- 模型加载与推理：[model.py](file:///d:/fun-asr-nano-api/app/core/model.py)
- 接口路由：[routes.py](file:///d:/fun-asr-nano-api/app/api/routes.py)
- 音频工具：[audio.py](file:///d:/fun-asr-nano-api/app/utils/audio.py)
- 部署文件：[Dockerfile](file:///d:/fun-asr-nano-api/deploy/Dockerfile)、[docker-compose.yml](file:///d:/fun-asr-nano-api/docker-compose.yml)
- 测试脚本：[test_api.py](file:///d:/fun-asr-nano-api/test_api.py)

## 技术栈与架构
- 框架：FastAPI（异步、高性能）
- 模型：Fun-ASR-Nano-2512（多语言、低延迟），通过 FunASR 的 `AutoModel` 加载
- 并发：`ThreadPoolExecutor` 控制并发，避免阻塞事件循环
- 流式：WebSocket 接收二进制音频帧，利用模型的 `cache` 参数实现增量识别（如模型支持）
- 部署：Docker + Compose；支持映射宿主机模型权重目录，GPU 加速

## 快速开始

### 1. 准备模型权重（宿主机）
将 `Fun-ASR-Nano-2512` 权重下载到宿主机 `./models/Fun-ASR-Nano-2512` 目录：

```bash
mkdir -p models
# 例如使用 git lfs（具体链接以官方提供为准）
git lfs install
# 从 ModelScope/HuggingFace 下载到 models/Fun-ASR-Nano-2512
# git clone <repo-url> models/Fun-ASR-Nano-2512
```

说明：部署时会将宿主机 `./models` 映射到容器 `/models`，并通过环境变量 `MODEL_DIR=/models/Fun-ASR-Nano-2512` 指定模型目录。

### 2. 启动服务（Docker Compose）

```bash
docker-compose up -d --build
```

- 服务启动后默认监听 `http://localhost:8000`
- 健康检查接口：`GET /health`

### 3. 本地开发（可选）
如需本地调试，需安装依赖（需具备合适的 Python/系统环境）：

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 接口说明

### REST：OpenAI 风格 `/v1/audio/transcriptions`
- 方法：POST（`multipart/form-data`）
- 参数：
  - `file` 必填，音频文件（建议 WAV/PCM；FunASR 支持多格式）
  - `model` 可选，默认 `fun-asr-nano-2512`
  - `language` 可选，默认 `auto`
  - `response_format` 可选，`json|text|verbose_json`，默认 `json`

示例（curl）：

```bash
curl http://localhost:8000/v1/audio/transcriptions \
  -F file=@/path/to/audio.wav \
  -F model="fun-asr-nano-2512" \
  -F language="auto" \
  -F response_format="json"
```

返回（示例）：

```json
{"text": "识别到的文本内容"}
```

更详细的返回：设置 `response_format=verbose_json`。

对应实现：请参考 [routes.py](file:///d:/fun-asr-nano-api/app/api/routes.py#L1-L48) 中的 `transcribe_audio`。

### WebSocket：流式 `/v1/audio/stream`
- 连接：`ws://localhost:8000/v1/audio/stream`
- 客户端发送：
  - 二进制音频帧（WAV/PCM chunk），服务端实时处理
  - 文本消息 `EOS` 表示本轮音频结束，触发最终结果输出
- 服务端返回：
  - 文本帧，JSON 格式：`{"text": "部分文本", "is_final": false}` 或最终 `true`

简单客户端示例（参见 [test_api.py](file:///d:/fun-asr-nano-api/test_api.py)）：

```python
import asyncio, websockets

async def send_audio(path):
    uri = "ws://localhost:8000/v1/audio/stream"
    async with websockets.connect(uri) as ws:
        with open(path, "rb") as f:
            while chunk := f.read(10240):
                await ws.send(chunk)
                print(await ws.recv())
        await ws.send("EOS")
        print(await ws.recv())

asyncio.run(send_audio("/path/to/audio.wav"))
```

对应实现：请参考 [routes.py](file:///d:/fun-asr-nano-api/app/api/routes.py#L50-L100) 与模型管理 [model.py](file:///d:/fun-asr-nano-api/app/core/model.py#L64-L89)。

## 并发与性能
- 并发控制：`MAX_CONCURRENT_REQUESTS`（默认 10），在 [config.py](file:///d:/fun-asr-nano-api/app/core/config.py) 中配置
- 推理执行：使用线程池释放 GIL，避免阻塞 FastAPI 事件循环
- 长音频建议：结合 VAD（语音活动检测）进行分段处理可显著降低显存与内存压力
- 设备选择：`DEVICE` 可设为 `cuda:0`（GPU）或 `cpu`

## 配置项（环境变量）
- `MODEL_DIR`：模型目录（示例 `/models/Fun-ASR-Nano-2512`）
- `DEVICE`：推理设备（`cuda:0` 或 `cpu`）
- `MAX_CONCURRENT_REQUESTS`：并发上限

在运行时由 [config.py](file:///d:/fun-asr-nano-api/app/core/config.py) 读取。

## 部署说明（GPU）
- Docker 镜像：见 [Dockerfile](file:///d:/fun-asr-nano-api/deploy/Dockerfile)
- Compose 配置：见 [docker-compose.yml](file:///d:/fun-asr-nano-api/docker-compose.yml)
- 需要在宿主机安装 `nvidia-container-toolkit` 并正确配置 GPU 驱动

## 测试
- REST 测试：`python test_api.py --file your.wav --mode rest`
- WS 测试：`python test_api.py --file your.wav --mode ws`

脚本详见 [test_api.py](file:///d:/fun-asr-nano-api/test_api.py)。

## 常见问题
- 权重未找到：确认宿主机 `./models/Fun-ASR-Nano-2512` 已映射到容器 `/models/Fun-ASR-Nano-2512`，且设置了 `MODEL_DIR`
- CUDA 不可用：检查驱动、CUDA 版本与容器运行参数；可临时切换 `DEVICE=cpu` 验证功能
- 音频格式：若为原始 PCM，请保证采样率（默认 16k）与编码格式；建议使用标准 WAV

## 维护与扩展
- 如需增强流式效果：可接入 VAD，或根据 FunASR 官方文档调整 `chunk_size`、`cache` 等参数
- 如需增加识别语言/热词：参考 FunASR `generate` 参数（如 `language`、`hotwords`）在 [model.py](file:///d:/fun-asr-nano-api/app/core/model.py#L46-L62) 中添加


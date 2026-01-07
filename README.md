# FunASR Nano 语音识别服务（默认中文）

语言切换： [中文](file:///d:/fun-asr-nano-api/README.md) | [English](file:///d:/fun-asr-nano-api/README_en.md)

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
- 部署文件：[Dockerfile](file:///d:/fun-asr-nano-api/deploy/Dockerfile)、[docker-compose.yml](file:///d:/fun-asr-nano-api/docker-compose.yml)
- 测试脚本：[test_api.py](file:///d:/fun-asr-nano-api/test_api.py)

## 快速开始

### 1. 准备模型权重（宿主机）
将 `Fun-ASR-Nano-2512` 权重下载到宿主机 `./models/Fun-ASR-Nano-2512` 目录：

```bash
mkdir -p models
git lfs install
# git clone <repo-url> models/Fun-ASR-Nano-2512
```

### 2. 启动服务（Docker Compose）

```bash
docker-compose up -d --build
```

服务地址：`http://localhost:8000`；健康检查：`GET /health`

## 接口说明

### REST：`/v1/audio/transcriptions`

```bash
curl http://localhost:8000/v1/audio/transcriptions \
  -F file=@/path/to/audio.wav \
  -F model="fun-asr-nano-2512" \
  -F language="auto" \
  -F response_format="json"
```

返回：`{"text": "识别到的文本内容"}`；详细返回使用 `verbose_json`。

### WebSocket：`/v1/audio/stream`
- 发送二进制音频帧；发送文本 `EOS` 结束并返回最终结果。

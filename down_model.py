#模型下载
from modelscope import snapshot_download
model_dir = snapshot_download('FunAudioLLM/Fun-ASR-Nano-2512',cache_dir='D:\models')
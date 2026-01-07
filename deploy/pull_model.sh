#!/usr/bin/env bash
set -euo pipefail
mkdir -p models
if ! command -v git >/dev/null 2>&1; then
  echo "git not found"; exit 1
fi
git lfs install
REPO_URL=${1:-https://www.modelscope.cn/FunAudioLLM/Fun-ASR-Nano-2512.git}
TARGET_DIR=${2:-models/Fun-ASR-Nano-2512}
if [ -d "$TARGET_DIR/.git" ]; then
  echo "repo exists"; exit 0
fi
git clone "$REPO_URL" "$TARGET_DIR"
echo "done"

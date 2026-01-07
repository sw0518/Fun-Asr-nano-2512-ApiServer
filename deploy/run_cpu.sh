#!/usr/bin/env bash
set -euo pipefail
DEVICE=cpu docker compose up -d --build
docker compose logs -f --tail=50

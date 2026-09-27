#!/bin/bash
# QuantDinger 单项目启动
# 用法: bash start.sh

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"

# Ensure Colima is running
if ! colima status &>/dev/null; then
  echo "🔄 启动 Colima..."
  colima start
fi

# Start QuantDinger
cd "$DIR"
echo "🔄 启动 QuantDinger Docker Compose..."
docker-compose up -d --build

# Wait for healthy
echo "⏳ 等待容器 healthy..."
for i in $(seq 1 30); do
  HEALTHY=$(docker-compose ps --format json 2>/dev/null | grep -c '"running"' || echo "0")
  if [ "$HEALTHY" -ge 4 ]; then
    break
  fi
  sleep 2
done

# Verify
echo ""
curl -sf http://127.0.0.1:15000/api/health && echo "" || echo "❌ Backend not healthy"
echo "✅ QuantDinger 已启动 — 前端: http://127.0.0.1:8888 | 后端: http://127.0.0.1:15000/api/health"
#!/bin/bash

# =====================================================
# 私人金融分析师后端 - 停止后台服务脚本
# =====================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
LOG_FILE="logs/daemon.log"
PID_FILE="logs/docker-compose.pid"

# 日志函数
log_with_time() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

echo "=================================="
echo "🛑 停止后台服务"
echo "=================================="

# 停止Docker Compose服务
echo -e "${BLUE}[1/3]${NC} 停止Docker Compose服务..."
if [ -f "$COMPOSE_FILE" ] && [ -f "$ENV_FILE" ]; then
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    log_with_time "Docker Compose服务已停止"
else
    echo -e "${YELLOW}⚠️ 配置文件不存在${NC}"
fi

# 终止后台进程
echo -e "${BLUE}[2/3]${NC} 终止后台进程..."
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        echo "已终止进程 PID: $PID"
        log_with_time "已终止后台进程 PID: $PID"
    else
        echo "进程 PID: $PID 不存在"
    fi
    rm -f "$PID_FILE"
else
    echo "未找到PID文件"
fi

# 清理悬空容器
echo -e "${BLUE}[3/3]${NC} 清理环境..."
docker system prune -f > /dev/null 2>&1

echo ""
echo "📊 剩余Docker进程："
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "=================================="
echo -e "${GREEN}✅ 后台服务已完全停止${NC}"
echo "=================================="

log_with_time "后台服务完全停止" 
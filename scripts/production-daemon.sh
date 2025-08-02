#!/bin/bash

# =====================================================
# 私人金融分析师后端 - 持久化后台启动脚本
# 确保即使SSH连接断开也能持续运行
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

# 创建日志目录
mkdir -p logs

# 日志函数
log_with_time() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

echo "=================================="
echo "🚀 启动持久化后台服务"
echo "=================================="

# 检查环境变量文件
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ 未找到环境变量文件: $ENV_FILE${NC}"
    exit 1
fi

# 停止现有服务（如果有）
echo -e "${BLUE}[1/4]${NC} 停止现有服务..."
nohup docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down > /dev/null 2>&1

# 清理悬空容器和网络
echo -e "${BLUE}[2/4]${NC} 清理环境..."
docker system prune -f > /dev/null 2>&1

# 后台启动服务
echo -e "${BLUE}[3/4]${NC} 启动后台服务..."
log_with_time "开始启动生产环境后台服务"

# 使用nohup确保进程不受SIGHUP信号影响
nohup docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d \
    > logs/docker-compose.log 2>&1 &

# 记录进程ID
COMPOSE_PID=$!
echo $COMPOSE_PID > "$PID_FILE"

echo -e "${GREEN}✓${NC} 服务启动命令已在后台执行"
echo "进程ID: $COMPOSE_PID"
log_with_time "Docker Compose启动，PID: $COMPOSE_PID"

# 等待服务启动
echo -e "${BLUE}[4/4]${NC} 等待服务就绪..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
if docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps | grep -q "Up"; then
    echo -e "${GREEN}✅ 服务启动成功！${NC}"
    log_with_time "所有服务启动成功"
    
    # 显示服务状态
    echo ""
    echo "📊 服务状态："
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    
    echo ""
    echo "🌐 访问地址："
    echo "  - 后端API: http://localhost:8000"
    echo "  - API文档: http://localhost:8000/docs"
    echo "  - 健康检查: http://localhost:8000/health"
    
    echo ""
    echo "📋 管理命令："
    echo "  - 查看状态: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE ps"
    echo "  - 查看日志: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE logs -f"
    echo "  - 停止服务: docker-compose -f $COMPOSE_FILE --env-file $ENV_FILE down"
    echo "  - 重启服务: ./scripts/production-daemon.sh"
    echo "  - 监控服务: ./scripts/monitor.sh check"
    
    echo ""
    echo "📝 日志文件："
    echo "  - 后台日志: logs/docker-compose.log"
    echo "  - 守护进程日志: logs/daemon.log"
    echo "  - 进程ID文件: logs/docker-compose.pid"
    
else
    echo -e "${RED}❌ 服务启动失败${NC}"
    log_with_time "服务启动失败"
    echo "请检查日志: tail -f logs/docker-compose.log"
    exit 1
fi

echo ""
echo "=================================="
echo -e "${GREEN}🎉 持久化后台服务启动完成！${NC}"
echo "📡 即使SSH连接断开，服务也会继续运行"
echo "=================================="

log_with_time "持久化后台服务启动完成" 
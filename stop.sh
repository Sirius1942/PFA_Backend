#!/bin/bash

# 私人金融分析师系统停止脚本

echo "🛑 停止私人金融分析师系统..."

# 停止所有相关服务
echo "📦 停止Docker服务..."

# 停止完整部署
docker-compose -f docker-compose.full.yml down 2>/dev/null || echo "完整部署未运行"

# 停止后端服务
docker-compose down 2>/dev/null || echo "后端服务未运行"

# 停止前端容器（如果存在）
docker stop financial_frontend 2>/dev/null || echo "前端容器未运行"
docker rm financial_frontend 2>/dev/null || echo "前端容器已清理"

# 清理网络
echo "🧹 清理Docker网络..."
docker network rm financial_network 2>/dev/null || echo "网络已清理或不存在"

# 显示剩余的相关容器
echo "📋 检查剩余容器..."
docker ps -a | grep financial || echo "没有相关容器运行"

echo "✅ 系统已停止!"
echo ""
echo "💡 提示:"
echo "  重新启动: ./start.sh"
echo "  清理数据: docker system prune -f"

#!/bin/bash

# =====================================================
# 快速启动生产环境脚本
# =====================================================

cd "$(dirname "$0")/.."

echo "🚀 启动私人金融分析师后端生产环境..."

# 检查 .env.prod 文件
if [ ! -f ".env.prod" ]; then
    echo "❌ 未找到 .env.prod 文件"
    echo "📝 请先复制 docker/env.example.prod 为 .env.prod 并配置"
    exit 1
fi

# 启动服务
echo "📦 启动 Docker 容器..."
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

echo "⏳ 等待服务启动..."
sleep 30

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

echo "✅ 部署完成！"
echo "🌐 后端服务: http://localhost:8000"
echo "🗄️ 数据库: localhost:3307"
echo "📊 Redis: localhost:6379"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker-compose -f docker-compose.prod.yml logs -f"
echo "  停止服务: docker-compose -f docker-compose.prod.yml down"
echo "  重启服务: docker-compose -f docker-compose.prod.yml restart" 
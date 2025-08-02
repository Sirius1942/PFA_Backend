#!/bin/bash

# 私人金融分析师系统启动脚本（开发模式）

set -e

echo "🚀 启动私人金融分析师开发环境..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 创建网络（如果不存在）
echo "📡 创建Docker网络..."
docker network create financial_network 2>/dev/null || echo "网络已存在"

# 启动MySQL数据库
echo "🗄️ 启动MySQL数据库..."
docker-compose up -d mysql

# 等待MySQL启动
echo "⏳ 等待MySQL数据库启动..."
timeout 60 bash -c 'until docker exec financial_mysql mysqladmin ping -h localhost -u root -proot123 --silent; do sleep 2; done' || {
    echo "❌ MySQL数据库启动失败"
    exit 1
}

echo "✅ MySQL数据库已启动: localhost:3307"

# 启动后端开发服务器
echo "🔧 启动后端开发服务器..."
echo "📖 API文档地址: http://localhost:8000/docs"
echo ""
echo "🎯 使用以下命令启动后端："
echo "  uvicorn main:app --reload"
echo ""
echo "📋 常用命令:"
echo "  查看MySQL日志: docker-compose logs -f mysql"
echo "  停止MySQL: docker-compose down"
echo "  重启MySQL: docker-compose restart mysql"
echo ""
echo "🗄️ 数据库连接信息:"
echo "  主机: localhost"
echo "  端口: 3307"
echo "  数据库: financial_db"
echo "  用户: financial_user"
echo "  密码: financial123"
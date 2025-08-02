#!/bin/bash

# 私人金融分析师系统启动脚本

set -e

echo "🚀 启动私人金融分析师系统..."

# 检查Docker是否运行
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker未运行，请先启动Docker"
    exit 1
fi

# 检查前端项目是否存在
if [ ! -d "../private_financial_analyst_frontend" ]; then
    echo "❌ 前端项目目录不存在，请确保已正确拆分项目"
    exit 1
fi

# 创建网络（如果不存在）
echo "📡 创建Docker网络..."
docker network create financial_network 2>/dev/null || echo "网络已存在"

# 选择启动模式
echo "请选择启动模式："
echo "1) 开发模式 (后端API + 前端开发服务器)"
echo "2) 生产模式 (完整Docker部署)"
echo "3) 仅后端 (API服务)"

read -p "请输入选择 (1-3): " choice

case $choice in
    1)
        echo "🔧 启动开发模式..."
        
        # 启动后端
        echo "📦 启动后端服务..."
        docker-compose up -d backend
        
        # 等待后端启动
        echo "⏳ 等待后端服务启动..."
        timeout 30 bash -c 'until curl -f http://localhost:8000/health 2>/dev/null; do sleep 1; done' || {
            echo "❌ 后端服务启动失败"
            exit 1
        }
        
        echo "✅ 后端服务已启动: http://localhost:8000"
        
        # 启动前端开发服务器
        echo "🎨 启动前端开发服务器..."
        cd ../private_financial_analyst_frontend
        if [ ! -d "node_modules" ]; then
            echo "📦 安装前端依赖..."
            npm install
        fi
        
        echo "🎯 前端开发服务器启动中..."
        echo "前端地址: http://localhost:3000"
        echo "后端API文档: http://localhost:8000/docs"
        npm run dev
        ;;
        
    2)
        echo "🏗️ 启动生产模式..."
        
        # 构建并启动完整系统
        echo "📦 构建并启动所有服务..."
        docker-compose -f docker-compose.full.yml up -d --build
        
        # 等待服务启动
        echo "⏳ 等待服务启动..."
        sleep 10
        
        # 检查服务状态
        echo "🔍 检查服务状态..."
        docker-compose -f docker-compose.full.yml ps
        
        echo "✅ 系统已启动!"
        echo "前端应用: http://localhost:3000"
        echo "后端API: http://localhost:8000"
        echo "API文档: http://localhost:8000/docs"
        ;;
        
    3)
        echo "🔧 启动仅后端模式..."
        
        # 启动后端
        docker-compose up -d backend
        
        # 等待后端启动
        echo "⏳ 等待后端服务启动..."
        timeout 30 bash -c 'until curl -f http://localhost:8000/health 2>/dev/null; do sleep 1; done' || {
            echo "❌ 后端服务启动失败"
            exit 1
        }
        
        echo "✅ 后端服务已启动!"
        echo "API地址: http://localhost:8000"
        echo "API文档: http://localhost:8000/docs"
        ;;
        
    *)
        echo "❌ 无效选择"
        exit 1
        ;;
esac

echo ""
echo "🎉 启动完成!"
echo ""
echo "📋 常用命令:"
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo ""
echo "📁 项目文档:"
echo "  后端: ../private_financial_analyst_backend/README.md"
echo "  前端: ../private_financial_analyst_frontend/README.md"
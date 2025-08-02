#!/bin/bash

# =====================================================
# 安装systemd服务脚本
# =====================================================

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=================================="
echo "⚙️ 安装PFA Backend Systemd服务"
echo "=================================="

# 获取当前目录的绝对路径
CURRENT_DIR=$(pwd)
SERVICE_FILE="systemd/pfa-backend.service"

# 检查服务文件是否存在
if [ ! -f "$SERVICE_FILE" ]; then
    echo -e "${RED}❌ 服务文件不存在: $SERVICE_FILE${NC}"
    exit 1
fi

# 更新服务文件中的路径
echo -e "${BLUE}[1/4]${NC} 更新服务文件路径..."
sed -i "s|/root/cjscode/PFA_Backend|$CURRENT_DIR|g" "$SERVICE_FILE"

# 复制服务文件到systemd目录
echo -e "${BLUE}[2/4]${NC} 安装systemd服务..."
sudo cp "$SERVICE_FILE" /etc/systemd/system/

# 重新加载systemd配置
echo -e "${BLUE}[3/4]${NC} 重新加载systemd配置..."
sudo systemctl daemon-reload

# 启用服务（开机自启动）
echo -e "${BLUE}[4/4]${NC} 启用开机自启动..."
sudo systemctl enable pfa-backend.service

echo ""
echo -e "${GREEN}✅ Systemd服务安装完成！${NC}"
echo ""
echo "📋 管理命令："
echo "  启动服务: sudo systemctl start pfa-backend"
echo "  停止服务: sudo systemctl stop pfa-backend"
echo "  重启服务: sudo systemctl restart pfa-backend"
echo "  查看状态: sudo systemctl status pfa-backend"
echo "  查看日志: sudo journalctl -u pfa-backend -f"
echo "  禁用开机启动: sudo systemctl disable pfa-backend"
echo ""
echo "🎯 服务已配置为开机自启动，即使系统重启也会自动运行！" 
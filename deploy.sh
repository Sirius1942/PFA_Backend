#!/bin/bash

# =====================================================
# 私人金融分析师后端 - 生产环境部署脚本
# =====================================================

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"
ENV_EXAMPLE_FILE="docker/env.example.prod"
PROJECT_NAME="pfa_backend"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    log_info "检查系统依赖..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    log_success "系统依赖检查完成"
}

# 创建必要目录
create_directories() {
    log_info "创建必要的目录..."
    
    mkdir -p logs
    mkdir -p logs/nginx
    mkdir -p nginx/ssl
    
    log_success "目录创建完成"
}

# 检查环境变量文件
check_env_file() {
    log_info "检查环境变量配置..."
    
    if [ ! -f "$ENV_FILE" ]; then
        log_warning "未找到 $ENV_FILE 文件"
        
        if [ -f "$ENV_EXAMPLE_FILE" ]; then
            log_info "复制示例配置文件..."
            cp "$ENV_EXAMPLE_FILE" "$ENV_FILE"
            log_warning "请编辑 $ENV_FILE 文件，修改所有敏感配置！"
            read -p "按回车键继续，或者按 Ctrl+C 退出..." 
        else
            log_error "未找到示例配置文件 $ENV_EXAMPLE_FILE"
            exit 1
        fi
    fi
    
    log_success "环境变量文件检查完成"
}

# 构建镜像
build_images() {
    log_info "构建 Docker 镜像..."
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build --no-cache
    
    log_success "镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动服务..."
    
    # 先启动数据库
    log_info "启动数据库服务..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d mysql redis
    
    # 等待数据库就绪
    log_info "等待数据库就绪..."
    sleep 30
    
    # 启动后端服务
    log_info "启动后端服务..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d backend
    
    # 启动 Nginx（可选）
    if [ "$1" = "--with-nginx" ]; then
        log_info "启动 Nginx 服务..."
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d nginx
    fi
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    
    # 检查健康状态
    log_info "检查服务健康状态..."
    sleep 10
    
    # 检查后端健康状态
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_success "后端服务运行正常"
    else
        log_warning "后端服务可能未就绪，请稍后检查"
    fi
}

# 查看日志
show_logs() {
    log_info "显示服务日志..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs -f --tail=50
}

# 停止服务
stop_services() {
    log_info "停止服务..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    log_success "服务已停止"
}

# 清理
cleanup() {
    log_info "清理未使用的资源..."
    docker system prune -f
    log_success "清理完成"
}

# 备份数据
backup_data() {
    log_info "备份数据..."
    
    # 创建备份目录
    BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份数据库
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec -T mysql mysqldump -u financial_user -p财务数据库密码 financial_db > "$BACKUP_DIR/database.sql"
    
    # 备份配置文件
    cp "$ENV_FILE" "$BACKUP_DIR/"
    
    log_success "数据备份完成：$BACKUP_DIR"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  deploy [--with-nginx]  部署整个应用（可选启用 Nginx）"
    echo "  start [--with-nginx]   启动服务（可选启用 Nginx）"
    echo "  stop                   停止服务"
    echo "  restart                重启服务"
    echo "  status                 查看服务状态"
    echo "  logs                   查看日志"
    echo "  build                  重新构建镜像"
    echo "  backup                 备份数据"
    echo "  cleanup                清理未使用的资源"
    echo "  help                   显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy              # 部署应用（不启用 Nginx）"
    echo "  $0 deploy --with-nginx # 部署应用（启用 Nginx）"
    echo "  $0 logs                # 查看日志"
}

# 主函数
main() {
    case "${1:-help}" in
        deploy)
            check_dependencies
            create_directories
            check_env_file
            build_images
            start_services "$2"
            check_services
            log_success "部署完成！"
            ;;
        start)
            start_services "$2"
            check_services
            ;;
        stop)
            stop_services
            ;;
        restart)
            stop_services
            sleep 5
            start_services "$2"
            check_services
            ;;
        status)
            check_services
            ;;
        logs)
            show_logs
            ;;
        build)
            build_images
            ;;
        backup)
            backup_data
            ;;
        cleanup)
            cleanup
            ;;
        help)
            show_help
            ;;
        *)
            log_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 
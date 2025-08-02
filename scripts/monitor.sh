#!/bin/bash

# =====================================================
# 私人金融分析师后端 - 系统监控脚本
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
LOG_FILE="logs/monitor.log"

# 创建日志目录
mkdir -p logs

# 日志函数
log_with_time() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# 检查服务健康状态
check_service_health() {
    local service_name=$1
    local health_url=$2
    
    if curl -f "$health_url" >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service_name 运行正常"
        log_with_time "INFO: $service_name 健康检查通过"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name 异常"
        log_with_time "ERROR: $service_name 健康检查失败"
        return 1
    fi
}

# 检查容器状态
check_container_status() {
    echo -e "${BLUE}=== 容器状态检查 ===${NC}"
    
    # 获取容器状态
    local containers=$(docker-compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.State}}\t{{.Status}}")
    echo "$containers"
    
    # 检查是否有异常容器
    local unhealthy=$(docker-compose -f "$COMPOSE_FILE" ps | grep -v "Up" | grep -v "Name" | wc -l)
    
    if [ "$unhealthy" -gt 0 ]; then
        echo -e "${RED}发现 $unhealthy 个异常容器${NC}"
        log_with_time "WARNING: 发现 $unhealthy 个异常容器"
        return 1
    else
        echo -e "${GREEN}所有容器运行正常${NC}"
        log_with_time "INFO: 所有容器运行正常"
        return 0
    fi
}

# 检查服务健康状态
check_services_health() {
    echo -e "${BLUE}=== 服务健康检查 ===${NC}"
    
    local all_healthy=true
    
    # 检查后端服务
    if ! check_service_health "后端服务" "http://localhost:8000/health"; then
        all_healthy=false
    fi
    
    # 检查数据库连接
    if docker-compose -f "$COMPOSE_FILE" exec -T mysql mysqladmin ping -h localhost >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} MySQL 数据库连接正常"
        log_with_time "INFO: MySQL 数据库连接正常"
    else
        echo -e "${RED}✗${NC} MySQL 数据库连接异常"
        log_with_time "ERROR: MySQL 数据库连接异常"
        all_healthy=false
    fi
    
    # 检查 Redis 连接
    if docker-compose -f "$COMPOSE_FILE" exec -T redis redis-cli ping >/dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Redis 连接正常"
        log_with_time "INFO: Redis 连接正常"
    else
        echo -e "${RED}✗${NC} Redis 连接异常"
        log_with_time "ERROR: Redis 连接异常"
        all_healthy=false
    fi
    
    return $all_healthy
}

# 检查系统资源
check_system_resources() {
    echo -e "${BLUE}=== 系统资源检查 ===${NC}"
    
    # 内存使用
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    echo "内存使用率: ${memory_usage}%"
    
    if (( $(echo "$memory_usage > 80" | bc -l) )); then
        echo -e "${RED}⚠️ 内存使用率过高${NC}"
        log_with_time "WARNING: 内存使用率过高: ${memory_usage}%"
    fi
    
    # 磁盘使用
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    echo "磁盘使用率: ${disk_usage}%"
    
    if [ "$disk_usage" -gt 80 ]; then
        echo -e "${RED}⚠️ 磁盘使用率过高${NC}"
        log_with_time "WARNING: 磁盘使用率过高: ${disk_usage}%"
    fi
    
    # CPU 负载
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    echo "CPU 负载: $load_avg"
    
    # Docker 容器资源使用
    echo -e "\nDocker 容器资源使用:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
}

# 检查日志错误
check_logs_for_errors() {
    echo -e "${BLUE}=== 日志错误检查 ===${NC}"
    
    # 检查后端日志中的错误
    local error_count=$(docker-compose -f "$COMPOSE_FILE" logs backend --since 1h 2>/dev/null | grep -i "error\|exception\|failed" | wc -l)
    
    if [ "$error_count" -gt 0 ]; then
        echo -e "${RED}发现 $error_count 个错误日志${NC}"
        log_with_time "WARNING: 最近1小时发现 $error_count 个错误日志"
        
        # 显示最新的错误
        echo "最新错误日志:"
        docker-compose -f "$COMPOSE_FILE" logs backend --since 1h 2>/dev/null | grep -i "error\|exception\|failed" | tail -5
    else
        echo -e "${GREEN}最近1小时无错误日志${NC}"
        log_with_time "INFO: 最近1小时无错误日志"
    fi
}

# 生成监控报告
generate_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local report_file="logs/monitor_report_$(date '+%Y%m%d_%H%M%S').txt"
    
    {
        echo "=================================="
        echo "系统监控报告 - $timestamp"
        echo "=================================="
        echo ""
        
        echo "1. 容器状态:"
        docker-compose -f "$COMPOSE_FILE" ps
        echo ""
        
        echo "2. 系统资源:"
        echo "内存使用: $(free | grep Mem | awk '{printf "%.1f%%", $3/$2 * 100.0}')"
        echo "磁盘使用: $(df / | awk 'NR==2 {print $5}')"
        echo "CPU 负载: $(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')"
        echo ""
        
        echo "3. 服务健康状态:"
        curl -s http://localhost:8000/health || echo "后端服务异常"
        echo ""
        
        echo "4. 最新日志错误 (最近1小时):"
        docker-compose -f "$COMPOSE_FILE" logs backend --since 1h 2>/dev/null | grep -i "error\|exception\|failed" | tail -10
        echo ""
        
    } > "$report_file"
    
    echo "监控报告已生成: $report_file"
}

# 发送告警（可扩展为邮件、钉钉等）
send_alert() {
    local message=$1
    log_with_time "ALERT: $message"
    
    # 这里可以添加邮件、短信、钉钉等告警方式
    # 例如：
    # curl -X POST "https://your-webhook-url" -d "{\"text\":\"$message\"}"
}

# 主监控函数
run_monitoring() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "=================================="
    echo "开始系统监控检查 - $timestamp"
    echo "=================================="
    
    local overall_status=true
    
    # 检查容器状态
    if ! check_container_status; then
        overall_status=false
        send_alert "发现异常容器"
    fi
    
    echo ""
    
    # 检查服务健康状态
    if ! check_services_health; then
        overall_status=false
        send_alert "服务健康检查失败"
    fi
    
    echo ""
    
    # 检查系统资源
    check_system_resources
    
    echo ""
    
    # 检查日志错误
    check_logs_for_errors
    
    echo ""
    echo "=================================="
    if [ "$overall_status" = true ]; then
        echo -e "${GREEN}✅ 系统运行正常${NC}"
        log_with_time "INFO: 系统监控检查完成，运行正常"
    else
        echo -e "${RED}❌ 发现系统异常${NC}"
        log_with_time "ERROR: 系统监控检查完成，发现异常"
    fi
    echo "=================================="
}

# 显示帮助
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  check       执行一次完整监控检查"
    echo "  watch       持续监控（每5分钟检查一次）"
    echo "  report      生成监控报告"
    echo "  logs        查看监控日志"
    echo "  help        显示此帮助"
}

# 主函数
main() {
    case "${1:-check}" in
        check)
            run_monitoring
            ;;
        watch)
            echo "开始持续监控（每5分钟检查一次）..."
            echo "按 Ctrl+C 停止监控"
            while true; do
                run_monitoring
                echo "等待5分钟..."
                sleep 300
            done
            ;;
        report)
            generate_report
            ;;
        logs)
            if [ -f "$LOG_FILE" ]; then
                tail -f "$LOG_FILE"
            else
                echo "监控日志文件不存在"
            fi
            ;;
        help)
            show_help
            ;;
        *)
            echo "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 
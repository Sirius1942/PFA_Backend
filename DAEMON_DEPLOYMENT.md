# 私人金融分析师后端 - 持久化后台服务部署指南

## 🎯 概述

本指南说明如何确保私人金融分析师后端服务在后台持续运行，即使SSH连接断开或系统重启也不受影响。

## 🔧 持久化方案

### 方案1: 使用持久化脚本 (推荐)

**特点**: 使用nohup确保进程不受SIGHUP信号影响，即使SSH断开也继续运行

```bash
# 启动持久化后台服务
./scripts/production-daemon.sh

# 停止后台服务
./scripts/stop-daemon.sh
```

### 方案2: 使用Systemd服务 (最佳)

**特点**: 系统级服务管理，开机自启动，自动重启，完整的日志管理

```bash
# 1. 安装systemd服务
./scripts/install-systemd.sh

# 2. 使用systemd管理服务
sudo systemctl start pfa-backend     # 启动服务
sudo systemctl stop pfa-backend      # 停止服务
sudo systemctl restart pfa-backend   # 重启服务
sudo systemctl status pfa-backend    # 查看状态
sudo journalctl -u pfa-backend -f    # 查看日志
```

## 📋 服务管理命令

### 快速命令

```bash
# 启动后台服务（持久化）
./scripts/production-daemon.sh

# 停止后台服务
./scripts/stop-daemon.sh

# 查看服务状态
docker-compose -f docker-compose.prod.yml --env-file .env.prod ps

# 查看实时日志
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs -f

# 测试登录功能
./scripts/test-production-login.sh

# 系统监控
./scripts/monitor.sh check
```

### 日志文件位置

```bash
# 后台启动日志
tail -f logs/docker-compose.log

# 守护进程日志
tail -f logs/daemon.log

# 进程ID文件
cat logs/docker-compose.pid
```

## 🔍 验证服务持久性

### 测试1: SSH断开连接
```bash
# 1. 启动服务
./scripts/production-daemon.sh

# 2. 断开SSH连接
exit

# 3. 重新连接并检查
docker ps
```

### 测试2: 系统重启后自动启动
```bash
# 1. 安装systemd服务
./scripts/install-systemd.sh

# 2. 重启系统
sudo reboot

# 3. 检查服务是否自动启动
sudo systemctl status pfa-backend
```

## 📊 服务架构

```
┌─────────────────────────────────────────┐
│            持久化后台服务                 │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────┐  ┌─────────────┐      │
│  │   nohup     │  │  systemd    │      │
│  │   进程保护   │  │   服务管理   │      │
│  └─────────────┘  └─────────────┘      │
│                                         │
│  ┌─────────────────────────────────────┐│
│  │         Docker Compose              ││
│  │  ┌─────────┐ ┌─────────┐ ┌────────┐ ││
│  │  │Backend  │ │ MySQL   │ │ Redis  │ ││
│  │  │  :8000  │ │ :3307   │ │ :6379  │ ││
│  │  └─────────┘ └─────────┘ └────────┘ ││
│  │  ┌─────────┐                        ││
│  │  │ Nginx   │                        ││
│  │  │ :80/443 │                        ││
│  │  └─────────┘                        ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

## 🛡️ 重启策略

### Docker Compose重启策略
```yaml
restart: unless-stopped  # 除非手动停止，否则总是重启
```

### Systemd重启策略
```ini
Restart=on-failure  # 失败时重启
RestartSec=10       # 重启间隔10秒
```

## 🔧 故障排除

### 问题1: 服务启动失败
```bash
# 查看详细日志
tail -f logs/docker-compose.log
docker-compose -f docker-compose.prod.yml --env-file .env.prod logs backend
```

### 问题2: 权限问题
```bash
# 确保脚本有执行权限
chmod +x scripts/*.sh
```

### 问题3: 端口冲突
```bash
# 检查端口占用
netstat -tlnp | grep -E "(8000|3307|6379|80|443)"
```

### 问题4: 进程丢失
```bash
# 检查进程是否存在
ps aux | grep docker-compose
cat logs/docker-compose.pid
```

## ⚡ 性能优化

### 1. 资源限制
```yaml
# 在docker-compose.prod.yml中设置
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
```

### 2. 日志轮转
```bash
# 配置Docker日志轮转
# /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "100m",
    "max-file": "3"
  }
}
```

## 📱 监控和告警

### 系统监控
```bash
# 实时监控
./scripts/monitor.sh watch

# 生成报告
./scripts/monitor.sh report
```

### 健康检查
```bash
# API健康检查
curl http://localhost:8000/health

# 登录功能检查
./scripts/test-production-login.sh
```

## ✅ 部署检查清单

- [ ] 所有容器正常运行
- [ ] 重启策略已配置
- [ ] 持久化脚本可执行
- [ ] 日志文件可访问
- [ ] 健康检查通过
- [ ] Systemd服务已安装（可选）
- [ ] 开机自启动已启用（可选）
- [ ] 监控脚本正常工作

---

## 🎉 总结

通过以上配置，您的私人金融分析师后端服务现在可以：

- ✅ 在后台持续运行
- ✅ 不受SSH连接断开影响
- ✅ 系统重启后自动启动
- ✅ 服务异常时自动重启
- ✅ 完整的日志记录
- ✅ 便捷的管理命令

**推荐使用方案**: 
1. 日常使用: `./scripts/production-daemon.sh`
2. 生产环境: 安装systemd服务实现完全自动化管理 
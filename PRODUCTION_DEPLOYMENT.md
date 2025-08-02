# 私人金融分析师后端 - 生产环境部署指南

## 🎯 概述

这是一个基于 FastAPI 的私人金融分析师后端项目的生产环境部署指南。使用 Docker 容器化部署，包含后端应用、MySQL 数据库、Redis 缓存和 Nginx 反向代理。

## 🏗️ 架构说明

```
                    ┌──────────────┐
                    │    Nginx     │ :80/443
                    │ (反向代理)    │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │   Backend    │ :8000
                    │  (FastAPI)   │
                    └──────┬───────┘
                           │
                ┌──────────┼──────────┐
                │          │          │
         ┌──────▼───┐  ┌──▼────┐ ┌───▼────┐
         │  MySQL   │  │ Redis │ │ Logs   │
         │   :3307  │  │ :6379 │ │ Volume │
         └──────────┘  └───────┘ └────────┘
```

## 📋 前置要求

### 系统要求
- Linux 服务器 (Ubuntu 20.04+ 推荐)
- 至少 2GB RAM
- 至少 10GB 磁盘空间
- Docker 20.10+
- Docker Compose 2.0+

### 安装 Docker 和 Docker Compose

```bash
# 安装 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

## 🚀 快速部署

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd PFA_Backend
```

### 2. 配置环境变量
```bash
# 复制环境变量模板
cp docker/env.example.prod .env.prod

# 编辑配置文件（重要！）
nano .env.prod
```

**必须修改的配置项：**
- `SECRET_KEY`: 强密码，至少 32 位
- `MYSQL_ROOT_PASSWORD`: MySQL root 密码
- `MYSQL_PASSWORD`: MySQL 用户密码
- `OPENAI_API_KEY`: OpenAI API 密钥
- `TAVILY_API_KEY`: Tavily API 密钥

### 3. 一键部署
```bash
# 使用快速启动脚本
./scripts/production-start.sh

# 或使用完整部署脚本
./deploy.sh deploy
```

### 4. 验证部署
```bash
# 检查服务状态
docker-compose -f docker-compose.prod.yml ps

# 检查后端健康状态
curl http://localhost:8000/health

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend
```

## 🔧 详细部署步骤

### 步骤 1: 环境配置

#### 创建 .env.prod 文件
```bash
cp docker/env.example.prod .env.prod
```

#### 关键配置说明
```env
# 安全配置 - 必须修改
SECRET_KEY=your-super-secret-key-change-this-in-production-256-bits-long
ALGORITHM=HS256

# 数据库配置 - 必须修改密码
MYSQL_ROOT_PASSWORD=very-strong-root-password-123
MYSQL_PASSWORD=very-strong-user-password-456

# 外部服务 - 必须配置
OPENAI_API_KEY=your-openai-api-key
TAVILY_API_KEY=your-tavily-api-key
```

### 步骤 2: 构建和启动

#### 使用完整部署脚本
```bash
# 检查依赖并部署
./deploy.sh deploy

# 或者分步执行
./deploy.sh build    # 构建镜像
./deploy.sh start    # 启动服务
./deploy.sh status   # 检查状态
```

#### 手动部署
```bash
# 1. 构建镜像
docker-compose -f docker-compose.prod.yml build

# 2. 启动数据库
docker-compose -f docker-compose.prod.yml up -d mysql redis

# 3. 等待数据库就绪
sleep 30

# 4. 启动后端
docker-compose -f docker-compose.prod.yml up -d backend

# 5. 启动 Nginx（可选）
docker-compose -f docker-compose.prod.yml up -d nginx
```

## 🔍 监控和管理

### 查看服务状态
```bash
# 查看所有容器状态
docker-compose -f docker-compose.prod.yml ps

# 查看特定服务日志
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f mysql
docker-compose -f docker-compose.prod.yml logs -f redis

# 查看资源使用情况
docker stats
```

### 常用管理命令
```bash
# 重启服务
./deploy.sh restart

# 停止服务
./deploy.sh stop

# 备份数据
./deploy.sh backup

# 清理未使用资源
./deploy.sh cleanup
```

## 🔐 安全配置

### 1. 防火墙设置
```bash
# 只开放必要端口
sudo ufw allow 22      # SSH
sudo ufw allow 80      # HTTP
sudo ufw allow 443     # HTTPS
sudo ufw enable
```

### 2. SSL/HTTPS 配置
```bash
# 创建 SSL 证书目录
mkdir -p nginx/ssl

# 使用 Let's Encrypt 获取证书
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com

# 复制证书到 nginx/ssl 目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem nginx/ssl/key.pem
```

### 3. 数据库安全
- 使用强密码
- 限制数据库访问 IP
- 定期备份数据

## 📊 性能优化

### 1. 容器资源限制
在 `docker-compose.prod.yml` 中添加：
```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### 2. 数据库优化
- 调整 `database/mysql.cnf` 配置
- 监控慢查询日志
- 定期优化表

### 3. Redis 优化
- 调整 `database/redis.conf` 配置
- 监控内存使用
- 设置适当的过期策略

## 🔄 更新和维护

### 代码更新
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
./deploy.sh build

# 3. 重启服务
./deploy.sh restart
```

### 数据备份
```bash
# 自动备份
./deploy.sh backup

# 手动备份数据库
docker-compose -f docker-compose.prod.yml exec mysql mysqldump -u root -p financial_db > backup_$(date +%Y%m%d).sql
```

### 数据恢复
```bash
# 恢复数据库
docker-compose -f docker-compose.prod.yml exec -T mysql mysql -u root -p financial_db < backup_file.sql
```

## 🚨 故障排除

### 常见问题

#### 1. 容器启动失败
```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs backend

# 检查容器状态
docker-compose -f docker-compose.prod.yml ps
```

#### 2. 数据库连接失败
```bash
# 检查数据库状态
docker-compose -f docker-compose.prod.yml exec mysql mysqladmin ping

# 检查网络连接
docker network ls
docker network inspect pfa_backend_pfa_network
```

#### 3. 内存不足
```bash
# 检查系统资源
free -h
df -h

# 清理 Docker 资源
docker system prune -a
```

### 日志位置
- 应用日志: `./logs/`
- Nginx 日志: `./logs/nginx/`
- 容器日志: `docker-compose logs`

## 📱 访问地址

部署成功后，可以通过以下地址访问：

- **后端 API**: http://your-server:8000
- **API 文档**: http://your-server:8000/docs
- **健康检查**: http://your-server:8000/health
- **数据库**: your-server:3307
- **Redis**: your-server:6379

## 📞 技术支持

如果遇到问题，请检查：
1. 环境变量配置是否正确
2. 防火墙和端口设置
3. Docker 和 Docker Compose 版本
4. 系统资源是否充足
5. 网络连接是否正常

---

**注意**: 生产环境部署前，请务必：
- 修改所有默认密码
- 配置 HTTPS
- 设置防火墙
- 配置监控和日志
- 制定备份策略 
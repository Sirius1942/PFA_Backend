# 私人金融分析师项目拆分指南

## 拆分概述

本项目已成功拆分为两个独立的项目：

- **后端项目**: `private_financial_analyst_backend`
- **前端项目**: `private_financial_analyst_frontend`

## 项目结构

### 拆分前（原项目）
```
private_financial_analyst/
├── backend/           # 后端代码
├── frontend/          # 前端代码
├── database/          # 数据库相关
├── config/            # 配置文件
├── scripts/           # 脚本文件
├── agents/            # AI代理
├── tools/             # 工具
├── *.py              # Python脚本
└── ...               # 其他文件
```

### 拆分后

#### 后端项目 (`private_financial_analyst_backend/`)
```
private_financial_analyst_backend/
├── app/                    # FastAPI应用核心
│   ├── api/               # API路由
│   ├── auth/              # 认证相关
│   ├── core/              # 核心配置
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模式
│   ├── services/          # 业务逻辑
│   └── utils/             # 工具函数
├── agents/                # AI代理
├── auth/                  # 认证服务
├── config/                # 配置文件
├── database/              # 数据库脚本和数据
├── scripts/               # 数据收集脚本
├── tools/                 # 工具脚本
├── logs/                  # 日志文件
├── *.py                   # Python脚本文件
├── main.py               # 应用入口
├── init_db.py            # 数据库初始化
├── requirements.txt      # Python依赖
├── Dockerfile            # Docker构建文件
├── docker-compose.yml    # Docker编排
├── docker-compose.full.yml # 完整部署配置
├── start.sh              # 启动脚本
├── stop.sh               # 停止脚本
├── .gitignore            # Git忽略文件
└── README.md             # 项目文档
```

#### 前端项目 (`private_financial_analyst_frontend/`)
```
private_financial_analyst_frontend/
├── public/               # 静态资源
├── src/                  # 源代码
│   ├── api/             # API接口
│   ├── assets/          # 静态资源
│   ├── components/      # 公共组件
│   ├── router/          # 路由配置
│   ├── stores/          # 状态管理
│   ├── utils/           # 工具函数
│   ├── views/           # 页面组件
│   ├── App.vue         # 根组件
│   └── main.ts         # 应用入口
├── .env                 # 环境变量
├── .env.example         # 环境变量示例
├── package.json         # Node.js依赖
├── tsconfig.json        # TypeScript配置
├── vite.config.ts       # Vite配置
├── Dockerfile           # Docker构建文件
├── docker-compose.yml   # Docker编排
├── nginx.conf           # Nginx配置
├── start.sh             # 启动脚本
├── stop.sh              # 停止脚本
├── .gitignore           # Git忽略文件
└── README.md            # 项目文档
```

## 启动指南

### 快速启动

#### 方式1：使用启动脚本（推荐）
```bash
# 在后端项目目录
cd private_financial_analyst_backend
./start.sh

# 选择启动模式：
# 1) 开发模式 (推荐用于开发)
# 2) 生产模式 (Docker完整部署)
# 3) 仅后端 (只启动API服务)
```

#### 方式2：手动启动

**启动后端：**
```bash
cd private_financial_analyst_backend

# 方式1：Python直接运行
python main.py

# 方式2：Docker运行
docker-compose up -d
```

**启动前端：**
```bash
cd private_financial_analyst_frontend

# 开发模式
npm install
npm run dev

# 生产模式
docker-compose up -d
```

### 完整部署
```bash
cd private_financial_analyst_backend
docker-compose -f docker-compose.full.yml up -d --build
```

## 配置说明

### 后端配置

#### 环境变量 (`.env`)
```env
DATABASE_URL=sqlite:///./financial_db.sqlite
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
```

#### 主配置文件 (`config/config.json`)
包含系统基础配置设置。

### 前端配置

#### 环境变量 (`.env`)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=私人金融分析师
VITE_ENABLE_MOCK=false
```

## 端口说明

| 服务 | 默认端口 | 说明 |
|------|----------|------|
| 后端API | 8000 | FastAPI服务 |
| 前端应用 | 3000 | Vue开发服务器 |
| 前端生产 | 80 | Nginx静态服务器 |
| MySQL | 3307 | 数据库（可选） |
| PostgreSQL | 5432 | 数据库（可选） |

## 开发工作流

### 1. 开发环境
```bash
# 终端1：启动后端
cd private_financial_analyst_backend
python main.py

# 终端2：启动前端
cd private_financial_analyst_frontend
npm run dev
```

### 2. 代码提交
每个项目独立维护Git历史：
```bash
# 后端项目
cd private_financial_analyst_backend
git init
git add .
git commit -m "Initial backend commit"

# 前端项目
cd private_financial_analyst_frontend
git init
git add .
git commit -m "Initial frontend commit"
```

### 3. 部署
```bash
# 生产环境部署
cd private_financial_analyst_backend
docker-compose -f docker-compose.full.yml up -d --build
```

## API接口

### 后端API端点
- **基础URL**: `http://localhost:8000/api/v1`
- **文档**: `http://localhost:8000/docs`
- **健康检查**: `http://localhost:8000/health`

### 主要接口
- `/auth/login` - 用户登录
- `/auth/register` - 用户注册
- `/stocks/` - 股票数据
- `/agent/chat` - AI对话
- `/users/profile` - 用户资料

## 数据库

### SQLite（默认）
- 文件位置: `financial_db.sqlite`
- 适用于开发和小规模部署

### MySQL/PostgreSQL（可选）
- 通过Docker Compose配置
- 适用于生产环境

## 监控和日志

### 后端日志
- 位置: `logs/` 目录
- 格式: 结构化JSON日志

### 前端监控
- 浏览器开发者工具
- Vue DevTools

### Docker日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 故障排除

### 常见问题

1. **端口占用**
   ```bash
   # 检查端口占用
   lsof -i :8000
   lsof -i :3000
   
   # 修改端口配置
   # 后端: main.py 中的 port 参数
   # 前端: vite.config.ts 中的 server.port
   ```

2. **Docker网络问题**
   ```bash
   # 重建网络
   docker network rm financial_network
   docker network create financial_network
   ```

3. **依赖问题**
   ```bash
   # 后端依赖
   pip install -r requirements.txt
   
   # 前端依赖
   npm install
   ```

4. **数据库连接问题**
   ```bash
   # 检查数据库文件
   ls -la *.sqlite
   
   # 重新初始化数据库
   python init_db.py
   ```

## 性能优化

### 后端优化
- 使用uvicorn workers
- 数据库连接池
- API响应缓存
- 静态文件CDN

### 前端优化
- 代码分割
- 懒加载
- 资源压缩
- PWA缓存

## 安全考虑

### 后端安全
- JWT令牌过期时间
- CORS配置
- SQL注入防护
- 输入验证

### 前端安全
- XSS防护
- CSRF防护
- 安全头设置
- HTTPS强制

## 扩展指南

### 添加新功能
1. 后端：在 `app/api/` 中添加新路由
2. 前端：在 `src/views/` 中添加新页面
3. 数据库：更新模型和迁移脚本

### 集成第三方服务
1. 后端：添加新的服务类
2. 前端：更新API接口配置
3. 环境变量：添加新的配置项

## 维护指南

### 定期维护
- 依赖更新
- 安全补丁
- 性能监控
- 备份策略

### 版本管理
- 语义化版本控制
- 变更日志维护
- 发布标签管理

## 联系信息

如有问题或建议，请通过以下方式联系：
- 项目Issues
- 开发团队邮箱
- 技术文档Wiki

---

**注意**: 请在生产环境部署前，确保修改所有默认密钥和敏感配置！
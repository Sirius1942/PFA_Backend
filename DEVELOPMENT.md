# 开发指南

## 项目概述

私人金融分析师是一个基于AI的个人金融分析和投资助手系统，采用现代化的微服务架构。

### 技术栈

- **前端**: Vue 3 + TypeScript + Element Plus + Vite
- **后端**: FastAPI + SQLAlchemy + Pydantic
- **数据库**: MySQL 8.0
- **缓存**: Redis
- **认证**: JWT + RBAC权限控制
- **AI**: LangChain + OpenAI
- **部署**: Docker + Docker Compose

## 快速开始

### 环境要求

- Docker 20.10+
- Docker Compose 2.0+
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### 启动开发环境

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd private_financial_analyst
   ```

2. **配置环境变量**
   ```bash
   # 复制环境变量模板
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   
   # 编辑环境变量文件
   vim backend/.env  # 设置数据库、Redis、OpenAI等配置
   vim frontend/.env # 设置前端配置
   ```

3. **启动服务**
   ```bash
   # 使用开发脚本启动（推荐）
   ./start-dev.sh
   
   # 或者使用Docker Compose
   docker-compose up -d
   ```

4. **访问应用**
   - 前端应用: http://localhost:3000
   - 后端API: http://localhost:8000
   - API文档: http://localhost:8000/docs

## 开发脚本

项目提供了便捷的开发脚本 `start-dev.sh`：

```bash
# 正常启动
./start-dev.sh

# 重新构建并启动
./start-dev.sh --build

# 清理环境并重新开始
./start-dev.sh --clean

# 查看日志
./start-dev.sh --logs

# 停止服务
./start-dev.sh --stop
```

## 项目结构

```
private_financial_analyst/
├── backend/                 # FastAPI后端
│   ├── app/
│   │   ├── api/v1/         # API路由
│   │   ├── auth/           # 认证模块
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── api/           # API接口
│   │   ├── components/    # 组件
│   │   ├── router/        # 路由
│   │   ├── stores/        # 状态管理
│   │   ├── utils/         # 工具函数
│   │   └── views/         # 页面
│   ├── Dockerfile
│   ├── package.json
│   └── .env.example
├── database/               # 数据库脚本
│   └── init.sql
├── docker-compose/         # Docker配置
│   └── nginx.conf
├── docker-compose.yml      # 服务编排
├── start-dev.sh           # 开发脚本
└── README.md
```

## 本地开发

### 后端开发

1. **安装依赖**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **启动开发服务器**
   ```bash
   # 确保MySQL和Redis已启动
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

3. **数据库迁移**
   ```bash
   # 创建数据库表
   python -c "from app.database import init_db; init_db()"
   ```

### 前端开发

1. **安装依赖**
   ```bash
   cd frontend
   npm install
   ```

2. **启动开发服务器**
   ```bash
   npm run dev
   ```

3. **构建生产版本**
   ```bash
   npm run build
   ```

## API开发

### 添加新的API端点

1. 在 `backend/app/api/v1/` 下创建新的路由文件
2. 定义Pydantic模型用于请求/响应
3. 实现业务逻辑
4. 在 `router.py` 中注册路由

### API文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 数据库管理

### 连接数据库

```bash
# 使用Docker连接
docker-compose exec mysql mysql -u financial_user -p financial_db

# 本地连接
mysql -h localhost -P 3306 -u financial_user -p financial_db
```

### 数据库备份

```bash
# 备份
docker-compose exec mysql mysqldump -u financial_user -p financial_db > backup.sql

# 恢复
docker-compose exec -T mysql mysql -u financial_user -p financial_db < backup.sql
```

## 权限系统

### RBAC模型

- **用户(User)**: 系统用户
- **角色(Role)**: 用户角色（管理员、普通用户等）
- **权限(Permission)**: 具体权限（查看股票、管理用户等）

### 默认角色

- `admin`: 系统管理员，拥有所有权限
- `user`: 普通用户，基础功能权限

### 权限检查

```python
# 在API中使用权限装饰器
from app.auth.permissions import require_permission

@router.get("/admin/users")
@require_permission("manage_users")
async def get_users():
    pass
```

## 前端开发规范

### 组件开发

- 使用Vue 3 Composition API
- TypeScript类型定义
- 响应式设计，兼容移动端

### 状态管理

- 使用Pinia进行状态管理
- 按模块组织store

### 路由守卫

- 认证检查
- 权限验证
- 页面标题设置

## 测试

### 后端测试

```bash
cd backend
pytest tests/
```

### 前端测试

```bash
cd frontend
npm run test
```

## 部署

### 生产环境部署

1. 修改环境变量配置
2. 构建生产镜像
3. 使用Docker Compose部署

```bash
# 生产环境启动
docker-compose -f docker-compose.prod.yml up -d
```

## 监控和日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 健康检查

- 后端健康检查: http://localhost:8000/health
- 数据库连接检查: 在后端日志中查看

## 故障排除

### 常见问题

1. **数据库连接失败**
   - 检查MySQL服务是否启动
   - 验证数据库配置
   - 查看网络连接

2. **前端无法访问后端API**
   - 检查CORS配置
   - 验证API地址
   - 查看网络代理设置

3. **权限验证失败**
   - 检查JWT token是否有效
   - 验证用户权限配置
   - 查看认证中间件日志

### 调试技巧

- 使用浏览器开发者工具
- 查看Docker容器日志
- 使用API测试工具（Postman、curl）

## 贡献指南

1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 代码规范

- Python: 使用black格式化，flake8检查
- TypeScript: 使用Prettier格式化，ESLint检查
- 提交信息: 使用conventional commits格式

## 支持

如有问题，请：

1. 查看文档和FAQ
2. 搜索已有的Issues
3. 创建新的Issue
4. 联系开发团队

---

更多详细信息请参考项目README.md文件。
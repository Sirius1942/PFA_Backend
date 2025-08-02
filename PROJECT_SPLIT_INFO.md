# 私人金融分析师项目 - 拆分说明

此项目已被拆分为两个独立的项目：

## 项目结构

```
📁 private_financial_analyst/                  # 原项目（仅保留拆分说明）
├── private_financial_analyst_backend/         # 🔧 后端API项目
└── private_financial_analyst_frontend/        # 🎨 前端界面项目
```

## 独立项目说明

### 🔧 后端项目 (private_financial_analyst_backend)
- **技术栈**: FastAPI + SQLAlchemy + SQLite
- **功能**: API服务、数据库管理、AI代理、用户认证
- **启动**: `cd private_financial_analyst_backend && ./start.sh`
- **文档**: `private_financial_analyst_backend/README.md`

### 🎨 前端项目 (private_financial_analyst_frontend)  
- **技术栈**: Vue 3 + TypeScript + Element Plus + Vite
- **功能**: 用户界面、股票展示、AI交互、数据可视化
- **启动**: `cd private_financial_analyst_frontend && npm run dev`
- **文档**: `private_financial_analyst_frontend/README.md`

## 快速启动

### 开发模式
```bash
# 启动后端 (终端1)
cd private_financial_analyst_backend
./start.sh
# 选择模式1: 开发模式

# 启动前端 (终端2) 
cd private_financial_analyst_frontend
npm install
npm run dev
```

### 生产部署
```bash
cd private_financial_analyst_backend
docker-compose -f docker-compose.full.yml up -d --build
```

## 访问地址

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000  
- **API文档**: http://localhost:8000/docs

## 项目迁移完成 ✅

- ✅ 后端：包含所有API、数据库、AI代理、工具脚本
- ✅ 前端：包含完整的Vue应用和相关配置
- ✅ 独立部署：两个项目可以完全独立开发和部署
- ✅ 配置完整：各自包含完整的Docker、文档、脚本

## 注意事项

1. **环境配置**: 请检查各项目的环境变量配置
2. **端口设置**: 默认后端8000端口，前端3000端口
3. **数据库**: 后端使用SQLite，可切换到MySQL/PostgreSQL
4. **API连接**: 前端已配置连接到后端API

---

有问题请查看各项目的详细文档或联系开发团队。

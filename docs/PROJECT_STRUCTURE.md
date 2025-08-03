# 项目目录结构

## 📁 整理后的项目结构

```
private_financial_analyst_backend/
├── 🏗️ 核心应用
│   ├── main.py                     # FastAPI 应用入口
│   ├── app/                        # 应用核心代码
│   │   ├── api/v1/                 # API 路由
│   │   ├── auth/                   # 认证模块
│   │   ├── core/                   # 核心配置和数据库
│   │   ├── models/                 # 数据模型
│   │   ├── schemas/                # Pydantic 模式
│   │   ├── services/               # 业务逻辑服务
│   │   └── utils/                  # 工具函数
│   └── agents/                     # AI 代理模块
│
├── 🗄️ 数据和配置
│   ├── database/                   # 数据库相关文件
│   │   ├── init_db.py             # 数据库初始化脚本
│   │   ├── init.sql               # SQL 初始化文件
│   │   ├── (MySQL数据库用于股票数据存储)
│   │   └── migrations/            # 数据库迁移
│   ├── config/                     # 配置文件
│   └── logs/                       # 日志目录
│
├── 🧪 测试和工具
│   ├── tests/                      # 测试文件
│   │   ├── __init__.py
│   │   ├── test_agent.py          # AI 代理测试
│   │   ├── test_login_api.py      # 登录 API 测试
│   │   ├── test_system.py         # 系统测试
│   │   └── test_technical.py      # 技术指标测试
│   ├── tools/                      # 工具脚本
│   └── scripts/                    # 辅助脚本
│
├── 🐳 部署和运维
│   ├── docker-compose.yml         # Docker 编排
│   ├── start.sh                   # 启动脚本
│   ├── stop.sh                    # 停止脚本
│   └── requirements.txt           # Python 依赖
│
└── 📚 文档
    ├── docs/                       # 项目文档
    ├── README.md                   # 项目说明
    └── DEVELOPMENT.md              # 开发指南
```

## 🔧 整理内容

### ✅ **已移动的文件**
- **测试文件**: `test_*.py` → `tests/` 目录
- **数据库文件**: `init_db.py`, `init.sql` → `database/` 目录

### 🗑️ **已删除的文件**
- **MySQL 数据库**: 项目使用MySQL作为唯一数据库
- **项目拆分文档**: `PROJECT_SPLIT_*.md`
- **临时修复脚本**: `fix_*.py`, `add_realtime_data.py`
- **演示文件**: `demo.py`
- **拆分脚本**: `complete_split.sh`
- **Python 缓存**: 所有 `__pycache__/` 目录
- **重复目录**: 根目录的 `auth/`（与 `app/auth/` 重复）
- **空目录**: `migrations/`, `data/`, `temp_scripts/`

### 📦 **目录作用说明**

#### **🏗️ 应用核心**
- `main.py`: FastAPI 应用启动文件
- `app/`: 包含所有业务逻辑代码
- `agents/`: AI 助手和金融分析代理

#### **🗄️ 数据层**
- `database/`: 数据库初始化和迁移文件
- `config/`: 应用配置文件
- `logs/`: 运行时日志存储

#### **🧪 开发支持**
- `tests/`: 单元测试和集成测试
- `tools/`: 数据处理和分析工具
- `scripts/`: 自动化脚本

#### **🐳 部署运维**
- Docker 相关: `docker-compose.yml`
- 启动脚本: `start.sh`, `stop.sh`
- 依赖管理: `requirements.txt`

## 🎯 **整理效果**

### **✨ 优势**
1. **结构清晰**: 按功能分类，易于导航
2. **测试隔离**: 测试文件统一管理
3. **减少冗余**: 删除重复和临时文件
4. **符合规范**: 遵循 Python 项目最佳实践

### **📈 统计**
- **删除文件**: 51 个文件/目录
- **移动文件**: 6 个文件重新组织
- **新增文件**: 1 个（`tests/__init__.py`）

---
**整理时间**: 2025-08-02  
**整理内容**: 目录结构优化  
**状态**: ✅ 完成
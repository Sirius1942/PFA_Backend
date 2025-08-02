# 配置管理说明

## 📋 配置架构概述

本项目采用统一配置管理架构，主要配置文件为 `config/config.json`，通过 `app/core/config.py` 加载并提供给各个服务使用。

## 🔧 配置文件结构

### config/config.json

```json
{
  "openai": {
    "api_key": "sk-xxx",                    // OpenAI API密钥
    "base_url": "http://116.63.86.12:3000/v1/",  // API服务地址
    "model": "gpt-4.1",                     // 使用的模型
    "temperature": 0.7,                     // 温度参数
    "max_tokens": 4000,                     // 最大令牌数
    "timeout": 30,                          // 超时时间
    "retry_attempts": 3                     // 重试次数
  },
  "database": {
    "url": "mysql+pymysql://financial_user:financial123@localhost:3307/financial_db",
    "echo": false,                          // 是否输出SQL日志
    "backup_path": "./database/backup/"     // 备份路径
  },
  "tavily": {
    "api_key": "tvly-xxx"                   // Tavily搜索API密钥
  },
  "data_sources": {
    "eastmoney": {                          // 东方财富数据源配置
      "base_url": "http://push2.eastmoney.com/api/qt/clist/get",
      "headers": {...},
      "params": {...}
    }
  },
  "stock_analysis": {
    "technical_indicators": ["MA", "MACD", "RSI", "BOLL", "KDJ"],
    "fundamental_metrics": ["PE", "PB", "ROE", "ROA", "EPS"],
    "risk_metrics": ["Beta", "Sharpe", "MaxDrawdown", "Volatility"]
  },
  "logging": {
    "level": "INFO",                        // 日志级别
    "file": "./logs/quant_agent.log",       // 日志文件路径
    "max_size": "10MB",                     // 最大日志文件大小
    "backup_count": 5                       // 日志文件备份数量
  }
}
```

### app/core/config.py

通过 `Settings` 类管理配置，自动从 `config.json` 加载配置项：

```python
class Settings(BaseSettings):
    # 自动从config.json读取OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # 自动从config.json读取数据库配置
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
```

## 🚀 配置加载流程

1. **初始化时**: `Settings.__init__()` 调用 `load_config_json()` 读取配置文件
2. **配置映射**: 将JSON配置映射到相应的Settings字段
3. **环境变量**: 支持通过环境变量或.env文件覆盖配置
4. **默认值**: 未配置项使用合理的默认值

## 📊 配置使用方式

### 在服务中使用

```python
from app.core.config import settings

class AIAssistantService:
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_base_url = settings.OPENAI_BASE_URL
        self.model_name = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
```

### 在Agent中使用

```python
# agents/financial_agent.py 直接读取config.json
def __init__(self, config_path: str = "config/config.json"):
    with open(config_path, 'r', encoding='utf-8') as f:
        self.config = json.load(f)
```

## ⚙️ 配置验证

可以使用以下脚本验证配置是否正确加载：

```bash
python -c "
from app.core.config import settings
from app.services.ai_service import ai_service
print(f'AI配置: {settings.OPENAI_API_KEY is not None}')
print(f'数据库: {settings.DATABASE_URL}')
print(f'LLM可用: {ai_service.llm is not None}')
"
```

## 🔐 安全考虑

1. **敏感信息**: API密钥等敏感信息应通过环境变量覆盖
2. **版本控制**: 确保config.json中的敏感信息不会提交到代码仓库
3. **权限控制**: 限制配置文件的访问权限

## 📝 配置优先级

1. 环境变量 (最高优先级)
2. .env文件
3. config.json
4. 代码中的默认值 (最低优先级)

## 🛠️ 故障排除

### AI服务不可用
- 检查config.json中openai.api_key是否正确
- 确认openai.base_url网络可达
- 查看服务启动日志中的配置加载信息

### 数据库连接失败
- 验证config.json中database.url格式
- 确认MySQL服务运行状态
- 检查网络连接和防火墙设置

## 📈 最近更新

- **2025-08-02**: 统一配置管理，从config.json读取配置
- **2025-08-02**: 修复AI服务LangChain调用问题
- **2025-08-02**: 更新数据库配置为MySQL格式
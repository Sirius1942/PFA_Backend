# AI助手CLI测试指南

## 🚀 环境状态

### 服务状态
- ✅ 数据库: MySQL运行正常 (localhost:3307)
- ✅ 后端服务: FastAPI运行正常 (http://localhost:8000)
- ✅ API文档: http://localhost:8000/docs
- ✅ 健康检查: http://localhost:8000/health

### 测试用户
- **管理员账号**: admin / admin123
- **普通用户账号**: test / test123

## 📋 可用测试脚本

### 1. 快速健康检查
```bash
python quick_test.py
```
功能：测试基础接口是否正常运行

### 2. Admin登录权限测试
```bash
python admin_login_test.py
```
功能：
- 演示admin账号登录流程
- 获取完整的权限token
- 验证token有效性
- 测试各种需要认证的接口
- 显示详细的token信息

### 3. 完整CLI测试工具
```bash
python cli_test.py [选项] [命令]
```

#### 基本选项
- `--url`: API服务地址 (默认: http://localhost:8000)
- `--username`: 用户名 (默认: admin)
- `--password`: 密码 (默认: admin123)

#### 可用命令

##### 聊天对话
```bash
# 基本聊天
python cli_test.py --username admin --password admin123 chat "你好，请介绍一下你的功能"

# 带股票代码的聊天
python cli_test.py --username admin --password admin123 chat "分析一下这只股票" --stock 000001
```

##### 股票分析 (⚠️ 当前有问题)
```bash
# 技术分析
python cli_test.py --username admin --password admin123 stock 000001 --type technical

# 基本面分析
python cli_test.py --username admin --password admin123 stock 000001 --type fundamental

# 综合分析
python cli_test.py --username admin --password admin123 stock 000001 --type comprehensive
```

##### 市场洞察
```bash
# 市场概览
python cli_test.py --username admin --password admin123 market --type overview

# 市场趋势
python cli_test.py --username admin --password admin123 market --type trend

# 热点分析
python cli_test.py --username admin --password admin123 market --type hotspots
```

##### 智能建议
```bash
python cli_test.py --username admin --password admin123 suggestions
```

##### 交互模式
```bash
python cli_test.py --username admin --password admin123 interactive
```

### 3. 用户管理
```bash
# 创建测试用户
python create_test_user.py

# 查看用户列表
python create_test_user.py list
```

## 🧪 测试结果

### ✅ 正常功能
1. **基础服务**: 健康检查、根接口、API文档
2. **用户认证**: 登录功能正常
3. **AI聊天**: 基本对话功能正常
4. **权限控制**: 需要认证的接口正确返回401

### ⚠️ 需要修复的问题
1. **股票分析接口**: 存在'stock_code'错误，需要检查AI服务实现
2. **市场洞察**: 未测试，可能存在类似问题
3. **智能建议**: 未测试，可能存在类似问题

## 🔧 开发建议

### 1. 修复AI服务
检查 `app/services/ai_service.py` 中的股票分析方法，确保参数传递正确。

### 2. 完善错误处理
在AI服务中添加更好的错误处理和日志记录。

### 3. 添加更多测试用例
为每个API接口创建详细的测试用例。

## 📖 API文档

访问 http://localhost:8000/docs 查看完整的API文档，包括：
- 认证接口
- 用户管理
- 股票数据
- AI助手
- 数据采集

## 🚦 服务管理

### 启动服务
```bash
# 启动数据库和后端
./start.sh

# 或手动启动后端
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 停止服务
```bash
./stop.sh
```

### 查看日志
```bash
# 查看数据库日志
docker-compose logs -f mysql

# 查看后端日志
# 在运行uvicorn的终端查看
```

## 🎫 Token获取和使用

### 获取Admin Token
```bash
# 运行admin登录测试，获取完整token信息
python admin_login_test.py
```

### 快速获取Token
使用 `get_token.py` 快速获取admin认证token：

```bash
# 获取token并显示使用方法
python get_token.py

# 静默模式（只输出token）
python get_token.py --quiet

# 导出为环境变量
python get_token.py --export
```

### 完整集成示例
使用 `token_usage_example.py` 查看完整的token集成演示：

```bash
# 运行完整演示
python token_usage_example.py
```

该脚本展示了：
- 如何创建带认证的API客户端类
- 自动token管理和请求头设置
- 各种API接口的调用方法
- 错误处理和异常情况
- 实际项目集成指南

### 手动使用Token
```bash
# 使用curl命令测试API（替换YOUR_TOKEN为实际token）
curl -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"message":"你好"}' \
     http://localhost:8000/api/v1/assistant/chat
```

### 在Python脚本中使用Token
```python
import requests

# 设置认证头
headers = {
    "Authorization": "Bearer YOUR_TOKEN",
    "Content-Type": "application/json"
}

# 调用API
response = requests.post(
    "http://localhost:8000/api/v1/assistant/chat",
    json={"message": "你好"},
    headers=headers
)
```

## 💡 使用技巧

1. **先获取token**: 使用 `admin_login_test.py` 获取有效的认证token
2. **交互模式最适合手工测试**: 使用 `interactive` 命令进行连续对话测试
3. **先测试基础功能**: 使用 `quick_test.py` 确保服务正常
4. **查看详细错误**: 在API文档页面测试接口可以看到详细的错误信息
5. **检查服务状态**: 如果测试失败，先检查 http://localhost:8000/health
6. **复制token**: 从admin_login_test.py的输出中复制完整token用于其他工具

## 🐛 故障排除

### 服务无法启动
1. 检查端口8000是否被占用: `lsof -i :8000`
2. 检查数据库是否运行: `docker ps | grep mysql`
3. 检查配置文件: `config/config.json`

### 认证失败
1. 确保用户已创建: `python create_test_user.py list`
2. 检查用户名密码是否正确
3. 查看API文档中的认证要求

### AI功能异常
1. 检查OpenAI配置是否正确
2. 查看服务日志中的错误信息
3. 测试基础聊天功能是否正常
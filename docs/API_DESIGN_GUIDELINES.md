# 私人金融分析师API设计规范

## 🎯 **后端关注点**

### **核心原则**
- ✅ **接口合理性**: RESTful设计，语义清晰
- ✅ **功能完备性**: 覆盖业务全流程
- ✅ **数据一致性**: 统一的响应格式
- ✅ **安全性**: 认证授权、数据验证
- ✅ **性能**: 响应时间、并发处理
- ❌ **前端适配**: 移动端适配由前端负责

## 📋 **API设计规范**

### **1. RESTful 设计原则**
```
GET     /api/v1/stocks/{id}           # 获取单个资源
GET     /api/v1/stocks                # 获取资源列表
POST    /api/v1/stocks                # 创建资源
PUT     /api/v1/stocks/{id}           # 更新整个资源
PATCH   /api/v1/stocks/{id}           # 部分更新资源
DELETE  /api/v1/stocks/{id}           # 删除资源
```

### **2. 统一响应格式**
```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**错误响应格式**:
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": ["股票代码不能为空"],
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### **3. 分页规范**
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [],
    "pagination": {
      "page": 1,
      "size": 20,
      "total": 100,
      "pages": 5
    }
  }
}
```

### **4. 认证授权**
- **JWT Bearer Token**: `Authorization: Bearer <token>`
- **权限控制**: 基于角色的访问控制(RBAC)
- **接口权限**: `@require_permission(Permissions.XXX)`

## 🔍 **当前接口完备性分析**

### **✅ 已实现功能**
1. **用户认证** (7个接口)
   - 注册、登录、登出
   - 密码重置、令牌刷新
   - 用户资料管理

2. **股票数据** (10个接口)
   - 股票搜索、基础信息
   - 实时行情、历史K线
   - 自选股管理
   - 市场概览、行业数据

3. **AI助手** (5个接口)
   - 智能对话、股票分析
   - 市场洞察、对话历史
   - 智能建议

4. **用户管理** (6个接口)
   - 用户信息、密码修改
   - 角色管理

### **❌ 缺失功能分析**

#### **1. 系统管理接口**
```
GET     /api/v1/system/health         # 系统健康检查
GET     /api/v1/system/stats          # 系统统计信息
GET     /api/v1/system/logs           # 系统日志查看
POST    /api/v1/system/cache/clear    # 清除缓存
```

#### **2. 数据同步接口**
```
POST    /api/v1/sync/stocks           # 同步股票基础数据
POST    /api/v1/sync/realtime         # 同步实时行情
GET     /api/v1/sync/status           # 同步状态查询
```

#### **3. 报表导出接口**
```
GET     /api/v1/reports/portfolio     # 投资组合报告
GET     /api/v1/reports/analysis      # 分析报告导出
POST    /api/v1/reports/custom        # 自定义报表
```

#### **4. 消息通知接口**
```
GET     /api/v1/notifications         # 获取通知列表
POST    /api/v1/notifications/mark    # 标记已读
POST    /api/v1/notifications/settings # 通知设置
```

#### **5. 交易模拟接口**
```
POST    /api/v1/trading/buy           # 模拟买入
POST    /api/v1/trading/sell          # 模拟卖出
GET     /api/v1/trading/portfolio     # 模拟投资组合
GET     /api/v1/trading/history       # 交易历史
```

## 📊 **接口优化建议**

### **1. 当前接口问题**

#### **路径重复问题**
```bash
# 当前有问题的路径
/api/v1/stocks/stocks/info/{stock_code}    # 重复stocks
/api/v1/users/users/me                     # 重复users

# 应该优化为
/api/v1/stocks/info/{stock_code}
/api/v1/users/me
```

#### **缺少批量操作**
```bash
# 缺少批量接口
POST    /api/v1/stocks/realtime/batch  # 批量获取实时行情
POST    /api/v1/watchlist/batch        # 批量添加自选股
DELETE  /api/v1/watchlist/batch        # 批量删除自选股
```

### **2. 数据验证规范**
```python
# 输入验证
class StockCodeValidator:
    pattern = r'^[0-9]{6}$'  # 6位数字
    markets = ['SH', 'SZ', 'BJ']

# 分页参数验证
class PaginationParams:
    page: int = Field(ge=1, description="页码")
    size: int = Field(ge=1, le=100, description="每页数量")
```

### **3. 错误码规范**
```python
class ErrorCodes:
    # 业务错误码
    STOCK_NOT_FOUND = 10001        # 股票不存在
    INSUFFICIENT_PERMISSION = 10002 # 权限不足
    ANALYSIS_FAILED = 10003        # 分析失败
    
    # 系统错误码
    DATABASE_ERROR = 20001         # 数据库错误
    EXTERNAL_API_ERROR = 20002     # 外部API错误
    CACHE_ERROR = 20003            # 缓存错误
```

## 🚀 **开发规则清单**

### **接口开发必检项**
- [ ] RESTful路径设计
- [ ] 统一响应格式
- [ ] 权限控制装饰器
- [ ] 参数验证（Pydantic）
- [ ] 错误处理和状态码
- [ ] API文档注释
- [ ] 单元测试覆盖

### **数据库操作规范**
- [ ] 使用事务处理
- [ ] 软删除设计
- [ ] 创建/更新时间字段
- [ ] 数据库索引优化
- [ ] 分页查询优化

### **安全规范**
- [ ] SQL注入防护
- [ ] XSS攻击防护
- [ ] 敏感数据加密
- [ ] 接口限流设计
- [ ] 日志记录规范

### **性能规范**
- [ ] 数据库连接池
- [ ] Redis缓存策略
- [ ] 异步IO处理
- [ ] 接口响应时间监控
- [ ] 内存使用优化

## 📝 **待办事项优先级**

### **高优先级**
1. 修复路径重复问题
2. 添加系统管理接口
3. 完善错误处理机制
4. 添加接口限流

### **中优先级**
1. 添加批量操作接口
2. 实现数据同步功能
3. 添加报表导出功能
4. 完善监控告警

### **低优先级**
1. 交易模拟功能
2. 消息通知系统
3. 性能优化
4. 接口文档完善

## 🔧 **开发工具推荐**

- **API测试**: Postman/Insomnia
- **文档生成**: FastAPI自动生成Swagger
- **代码质量**: pylint, black, isort
- **测试框架**: pytest, pytest-asyncio
- **性能监控**: prometheus, grafana

---
**注意**: 此文档应定期更新，确保与项目发展同步
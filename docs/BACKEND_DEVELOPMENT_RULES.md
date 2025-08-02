# 后端开发规则与规范

## 🎯 **后端职责边界**

### **✅ 后端关注事项**
- **接口设计合理性**: RESTful设计、语义清晰
- **功能完备性**: 业务逻辑完整、数据处理准确
- **数据安全性**: 认证授权、数据验证、SQL注入防护
- **性能优化**: 数据库查询、缓存策略、并发处理
- **系统稳定性**: 错误处理、异常恢复、监控告警
- **代码质量**: 结构清晰、注释完整、测试覆盖

### **❌ 非后端关注事项**
- **前端UI适配**: 移动端适配、响应式设计
- **用户体验**: 页面交互、动画效果
- **浏览器兼容**: CSS兼容性、JS兼容性
- **前端性能**: 页面加载速度、资源压缩

## 📋 **强制性开发规范**

### **1. API路由设计规范**

#### **正确示例**
```python
# ✅ 正确：子路由不设置prefix
router = APIRouter(tags=["股票数据"])

# ✅ 正确：主路由统一添加prefix
api_router.include_router(
    stocks_router,
    prefix="/stocks",
    tags=["股票数据"]
)
```

#### **错误示例**
```python
# ❌ 错误：子路由设置prefix导致重复
router = APIRouter(prefix="/stocks", tags=["股票数据"])
```

### **2. 响应格式标准**

#### **成功响应**
```json
{
  "code": 200,
  "message": "success", 
  "data": {},
  "timestamp": "2024-08-02T10:00:00Z"
}
```

#### **错误响应**
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": ["股票代码格式不正确"],
  "timestamp": "2024-08-02T10:00:00Z"
}
```

### **3. 权限控制规范**
```python
@router.post("/analyze-stock")
@require_permission(Permissions.USE_AI_ASSISTANT)  # 必须添加权限控制
async def analyze_stock(request: StockAnalysisRequest):
    pass
```

### **4. 参数验证规范**
```python
class StockRequest(BaseModel):
    stock_code: str = Field(regex=r'^[0-9]{6}$', description="6位股票代码")
    period: str = Field(default="1d", regex=r'^(1d|1w|1m)$')
    
    @validator('stock_code')
    def validate_stock_code(cls, v):
        if not v.isdigit() or len(v) != 6:
            raise ValueError('股票代码必须是6位数字')
        return v
```

## 🔒 **安全规范**

### **必须实现的安全措施**
1. **JWT认证**: 所有业务接口必须验证token
2. **权限控制**: 基于角色的访问控制(RBAC)
3. **输入验证**: 使用Pydantic严格验证所有输入
4. **SQL注入防护**: 使用ORM参数化查询
5. **敏感数据加密**: 密码、密钥等必须加密存储
6. **接口限流**: 防止恶意请求和DDoS攻击

### **禁止的不安全做法**
```python
# ❌ 禁止：直接字符串拼接SQL
query = f"SELECT * FROM users WHERE id = {user_id}"

# ❌ 禁止：明文存储密码
user.password = plain_password

# ❌ 禁止：不验证用户输入
def transfer_money(amount):  # 缺少类型和范围验证
    pass
```

## 📊 **数据库操作规范**

### **事务处理**
```python
@router.post("/transfer")
async def transfer_money(request: TransferRequest, db: Session = Depends(get_db)):
    try:
        # 必须使用事务
        db.begin()
        # 业务操作
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="操作失败")
```

### **软删除设计**
```python
class BaseModel(Base):
    __abstract__ = True
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)  # 软删除标记
```

### **数据库查询优化**
```python
# ✅ 正确：使用索引、分页、预加载
query = db.query(Stock)\
    .filter(Stock.is_deleted == False)\
    .options(joinedload(Stock.industry))\
    .offset((page - 1) * size)\
    .limit(size)
```

## 🚀 **性能规范**

### **缓存策略**
```python
from functools import lru_cache
import redis

# 内存缓存
@lru_cache(maxsize=100)
def get_stock_info(stock_code: str):
    pass

# Redis缓存
async def get_realtime_data(stock_code: str):
    cache_key = f"realtime:{stock_code}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)
    # 查询数据库并缓存
```

### **异步处理**
```python
# ✅ 正确：IO密集型操作使用异步
async def fetch_external_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

## 🧪 **测试规范**

### **必须测试的场景**
1. **接口功能测试**: 正常流程、边界条件
2. **权限验证测试**: 有权限、无权限、过期token
3. **参数验证测试**: 有效参数、无效参数、缺失参数
4. **异常处理测试**: 数据库异常、外部API异常
5. **并发测试**: 高并发场景下的数据一致性

### **测试示例**
```python
def test_stock_analysis_success():
    # 正常情况测试
    pass

def test_stock_analysis_invalid_code():
    # 异常参数测试  
    pass

def test_stock_analysis_no_permission():
    # 权限验证测试
    pass
```

## 📝 **代码质量规范**

### **命名规范**
```python
# ✅ 正确的命名
class StockAnalysisService:     # 类名：PascalCase
    def calculate_rsi(self):    # 方法名：snake_case
        max_price = 100         # 变量名：snake_case
        API_BASE_URL = "..."    # 常量：UPPER_SNAKE_CASE
```

### **注释规范**
```python
class StockService:
    """股票数据服务
    
    提供股票基础信息、实时行情、历史数据等功能
    """
    
    async def get_stock_info(self, stock_code: str) -> Optional[StockInfo]:
        """获取股票基础信息
        
        Args:
            stock_code: 6位股票代码
            
        Returns:
            股票信息对象，如果不存在返回None
            
        Raises:
            ValueError: 股票代码格式错误
            HTTPException: 外部API请求失败
        """
        pass
```

## 🔄 **开发流程规范**

### **新功能开发检查清单**
- [ ] 需求分析和接口设计
- [ ] 数据库设计（如需要）
- [ ] 编写接口实现
- [ ] 添加权限控制
- [ ] 编写参数验证
- [ ] 添加错误处理
- [ ] 编写单元测试
- [ ] 更新API文档
- [ ] 代码审查
- [ ] 部署测试

### **代码提交规范**
```bash
# 提交信息格式
feat: 添加股票分析AI接口
fix: 修复用户登录token过期问题  
docs: 更新API设计规范文档
refactor: 重构股票数据查询逻辑
test: 添加用户权限验证测试
```

## ⚠️ **常见错误提醒**

### **已修复的问题**
1. ✅ **路径重复问题**: `/api/v1/stocks/stocks/` → `/api/v1/stocks/`
2. ✅ **AI助手路由未注册**: 已添加到主路由
3. ✅ **导入路径错误**: 统一使用`app.core.deps`

### **需要持续关注的问题**
1. ⚠️ **错误响应格式不统一**: 需要全局统一
2. ⚠️ **缺少批量操作接口**: 影响前端性能
3. ⚠️ **接口限流未实现**: 存在安全风险
4. ⚠️ **监控告警不完善**: 问题发现不及时

## 📅 **定期审查机制**

### **每周检查项**
- API接口规范性审查
- 新增接口权限验证
- 代码质量和测试覆盖率
- 性能指标和错误日志

### **每月优化项**
- 数据库查询性能优化
- 缓存策略调整
- 接口响应时间分析
- 安全漏洞扫描

---
**创建日期**: 2024-08-02  
**最后更新**: 2024-08-02  
**下次审查**: 每周五下午进行规范检查

> 💡 **提醒**: 新团队成员入职时必须阅读此文档，老成员定期回顾更新
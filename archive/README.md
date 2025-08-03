# Archive 目录

这个目录包含了被归档的文件，这些文件之前使用SQLite数据库，但已被移除以确保项目只使用MySQL。

## 归档的文件

### Scripts (脚本)
- `data_collector.py` - 股票数据采集器（原使用SQLite）

### Tools (工具)
- `database_tools.py` - 数据库查询工具（原使用SQLite）
- `data_calculator.py` - 数据计算工具（原使用SQLite）

### Tests (测试)
- `test_technical.py` - 技术指标测试（原使用SQLite）
- `test_agent.py` - Agent测试（依赖SQLite工具）

### Agents (代理)
- `financial_agent.py` - 金融量化分析师Agent（依赖SQLite工具）

## 说明

这些文件已被移动到此目录，因为：
1. 项目决定只使用MySQL数据库
2. 需要移除所有SQLite依赖
3. 保留这些文件以备将来参考或重构

## 迁移状态

✅ **数据库迁移已完成** - 所有SQLite表结构都已成功迁移到MySQL：

| 原SQLite表 | 新MySQL表 | 模型文件 | 状态 |
|------------|-----------|----------|------|
| stock_info | stock_info | app/models/stock.py | ✅ 完成 |
| realtime_quotes | realtime_quotes | app/models/stock.py | ✅ 完成 |
| kline_data | kline_data | app/models/stock.py | ✅ 完成 |
| technical_indicators | technical_indicators | app/models/technical_indicators.py | ✅ 新增 |

✅ **功能服务已更新** - 所有业务功能都基于MySQL重新实现：
- 股票数据服务 (app/services/stock_service.py)
- AI助手服务 (app/services/ai_service.py) 
- 用户管理服务 (app/services/user_service.py)

## 如何恢复功能

如果需要恢复这些功能，建议：
1. 基于现有的MySQL服务重构，而不是直接改写SQLite代码
2. 参考现有的service层实现模式
3. 使用SQLAlchemy ORM而不是原生SQL
4. 集成到现有的FastAPI应用架构中
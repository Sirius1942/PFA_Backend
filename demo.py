#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融量化分析师Agent演示程序

展示Agent的完整功能，包括数据采集、查询分析和智能对话。

作者: Assistant
日期: 2024
"""

import os
import sys
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def demo_data_collection():
    """
    演示数据采集功能
    """
    print("\n" + "="*60)
    print("📊 数据采集演示")
    print("="*60)
    
    try:
        from scripts.data_collector import EastMoneyDataCollector
        
        print("🔄 初始化数据采集器...")
        collector = EastMoneyDataCollector()
        
        print("📋 创建数据库表结构...")
        collector._init_database()
        
        print("📈 采集示例股票数据...")
        # 采集几只知名股票的数据作为演示
        sample_stocks = [
            {'code': '000001', 'name': '平安银行', 'market': 'SZ'},
            {'code': '000002', 'name': '万科A', 'market': 'SZ'},
            {'code': '600000', 'name': '浦发银行', 'market': 'SH'},
            {'code': '600036', 'name': '招商银行', 'market': 'SH'},
            {'code': '000858', 'name': '五粮液', 'market': 'SZ'}
        ]
        
        # 保存股票基本信息
        for stock in sample_stocks:
            collector.save_stock_info(stock)
            print(f"  ✅ 已保存 {stock['code']} {stock['name']}")
        
        print("\n🎯 数据采集演示完成！")
        print("💡 提示：实际使用时可以采集更多股票数据")
        
        return True
        
    except Exception as e:
        print(f"❌ 数据采集演示失败: {e}")
        return False

def demo_database_tools():
    """
    演示数据库查询工具
    """
    print("\n" + "="*60)
    print("🔍 数据库查询工具演示")
    print("="*60)
    
    try:
        from tools.database_tools import StockDatabaseTools
        
        db_tools = StockDatabaseTools()
        
        print("\n1️⃣ 股票信息查询:")
        stocks = db_tools.get_stock_info()
        if stocks:
            for stock in stocks[:3]:
                print(f"  📋 {stock.get('code')} - {stock.get('name')} ({stock.get('market')})")
        else:
            print("  ⚠️ 暂无股票数据，请先运行数据采集")
        
        print("\n2️⃣ 股票搜索功能:")
        search_results = db_tools.search_stocks("银行", limit=3)
        if search_results:
            for stock in search_results:
                print(f"  🔍 {stock.get('code')} - {stock.get('name')}")
        else:
            print("  ⚠️ 未找到匹配的股票")
        
        print("\n3️⃣ 市场概览:")
        overview = db_tools.get_market_overview()
        if overview:
            print(f"  📊 更新时间: {overview.get('update_time', 'N/A')}")
            if 'market_distribution' in overview:
                for market in overview['market_distribution']:
                    print(f"  🏢 {market.get('market', 'N/A')}: {market.get('count', 0)} 只股票")
        else:
            print("  ⚠️ 暂无市场数据")
        
        print("\n🎯 数据库工具演示完成！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库工具演示失败: {e}")
        return False

def demo_financial_agent():
    """
    演示金融分析师Agent
    """
    print("\n" + "="*60)
    print("🤖 金融分析师Agent演示")
    print("="*60)
    
    try:
        from agents.financial_agent import FinancialQuantAgent
        
        print("🔄 初始化Agent...")
        agent = FinancialQuantAgent()
        
        # 演示查询列表
        demo_queries = [
            "查询平安银行的基本信息",
            "搜索包含'银行'的股票",
            "今日市场概况如何",
            "我们刚才查询了哪些股票？"  # 测试记忆功能
        ]
        
        print("\n🎭 开始对话演示:")
        for i, query in enumerate(demo_queries, 1):
            print(f"\n{i}️⃣ 用户: {query}")
            print("🤖 分析师: ", end="")
            
            try:
                response = agent.chat(query)
                # 限制输出长度以便演示
                if len(response) > 300:
                    response = response[:300] + "...[输出已截断]"
                print(response)
            except Exception as e:
                print(f"处理查询时出错: {e}")
            
            time.sleep(1)  # 稍作停顿
        
        print("\n📝 对话记忆测试:")
        memory_summary = agent.get_memory_summary()
        print(f"  {memory_summary}")
        
        print("\n🎯 Agent演示完成！")
        return True
        
    except Exception as e:
        print(f"❌ Agent演示失败: {e}")
        print("💡 请确保已正确配置API密钥")
        return False

def check_configuration():
    """
    检查配置文件
    """
    print("\n" + "="*60)
    print("⚙️ 配置检查")
    print("="*60)
    
    config_path = "config/config.json"
    
    if not os.path.exists(config_path):
        print(f"❌ 配置文件不存在: {config_path}")
        return False
    
    try:
        import json
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        print("✅ 配置文件加载成功")
        
        # 检查必要的配置项
        missing_keys = []
        
        # 检查OpenAI配置
        if 'openai' not in config or 'api_key' not in config['openai'] or not config['openai']['api_key'] or config['openai']['api_key'] == "your_openai_api_key":
            missing_keys.append('openai_api_key')
        
        # 检查Tavily配置
        if 'tavily' not in config or 'api_key' not in config['tavily'] or not config['tavily']['api_key'] or config['tavily']['api_key'] == "your_tavily_api_key":
            missing_keys.append('tavily_api_key')
        
        if missing_keys:
            print(f"⚠️ 缺少或未配置的API密钥: {', '.join(missing_keys)}")
            print("💡 请在config/config.json中配置正确的API密钥")
            return False
        
        print("✅ API密钥配置检查通过")
        return True
        
    except Exception as e:
        print(f"❌ 配置文件检查失败: {e}")
        return False

def main():
    """
    主演示程序
    """
    print("🚀 金融量化分析师Agent - 完整演示")
    print("=" * 80)
    print("本演示将展示以下功能：")
    print("1. 配置检查")
    print("2. 数据采集")
    print("3. 数据库查询工具")
    print("4. 智能分析Agent")
    print("=" * 80)
    
    # 检查配置
    if not check_configuration():
        print("\n❌ 配置检查失败，请先配置API密钥")
        print("📝 编辑 config/config.json 文件，填入正确的API密钥")
        return
    
    # 数据采集演示
    print("\n🔄 开始数据采集演示...")
    if demo_data_collection():
        print("✅ 数据采集演示成功")
    else:
        print("⚠️ 数据采集演示失败，但继续其他演示")
    
    # 数据库工具演示
    print("\n🔄 开始数据库工具演示...")
    if demo_database_tools():
        print("✅ 数据库工具演示成功")
    else:
        print("⚠️ 数据库工具演示失败")
    
    # Agent演示
    print("\n🔄 开始Agent演示...")
    if demo_financial_agent():
        print("✅ Agent演示成功")
    else:
        print("⚠️ Agent演示失败")
    
    print("\n" + "="*80)
    print("🎉 演示完成！")
    print("\n💡 使用提示：")
    print("  - 运行 'python agents/financial_agent.py' 启动交互式Agent")
    print("  - 运行 'python scripts/data_collector.py' 采集更多数据")
    print("  - 查看 README.md 了解详细使用说明")
    print("\n⚠️ 免责声明：")
    print("  本项目仅供学习研究使用，所有分析结果仅供参考，")
    print("  不构成投资建议。投资有风险，入市需谨慎。")
    print("="*80)

if __name__ == "__main__":
    main()
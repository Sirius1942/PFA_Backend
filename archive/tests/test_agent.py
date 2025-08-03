#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试金融Agent的功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from agents.financial_agent import FinancialQuantAgent

def test_agent():
    """
    测试Agent功能
    """
    print("🧪 测试金融量化分析师 Agent")
    print("=" * 50)
    
    try:
        # 初始化Agent
        agent = FinancialQuantAgent()
        print("✅ Agent初始化成功")
        
        # 测试查询
        test_queries = [
            "查询股票代码002379的基本信息",
            "分析股票002379",
            "002379的实时行情",
            "宏创控股的股票信息"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🔍 测试 {i}: {query}")
            print("-" * 30)
            
            try:
                response = agent.chat(query)
                print(f"📝 回复: {response}")
            except Exception as e:
                print(f"❌ 查询失败: {e}")
                
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_agent()
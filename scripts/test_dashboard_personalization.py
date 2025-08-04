#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试看板个性化功能
演示不同用户看到不同的看板数据
"""

import sys
import os
from pathlib import Path
import requests
import json
from typing import Dict, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

BASE_URL = "http://localhost:8000"

class DashboardTester:
    """看板个性化测试类"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> Optional[str]:
        """用户登录获取token"""
        print(f"\n🔐 正在登录用户: {username}")
        
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": username, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ 登录成功!")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    
    def get_dashboard_data(self, token: str) -> Optional[Dict[str, Any]]:
        """获取看板数据"""
        print("📊 正在获取看板数据...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = self.session.get(
            f"{self.base_url}/api/v1/stocks/dashboard",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ 获取看板数据成功!")
            return response.json()
        else:
            print(f"❌ 获取看板数据失败: {response.status_code} - {response.text}")
            return None
    
    def get_watchlist(self, token: str) -> Optional[list]:
        """获取用户自选股"""
        print("📋 正在获取自选股列表...")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = self.session.get(
            f"{self.base_url}/api/v1/stocks/watchlist",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ 获取自选股成功!")
            return response.json()
        else:
            print(f"❌ 获取自选股失败: {response.status_code} - {response.text}")
            return None
    
    def add_to_watchlist(self, token: str, stock_code: str, notes: str = None) -> bool:
        """添加股票到自选股"""
        print(f"➕ 正在添加股票到自选股: {stock_code}")
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {"stock_code": stock_code}
        if notes:
            data["notes"] = notes
        
        response = self.session.post(
            f"{self.base_url}/api/v1/stocks/watchlist",
            json=data,
            headers=headers
        )
        
        if response.status_code == 200:
            print(f"✅ 添加成功!")
            return True
        else:
            print(f"❌ 添加失败: {response.status_code} - {response.text}")
            return False
    
    def format_dashboard_data(self, data: Dict[str, Any], user_name: str) -> str:
        """格式化看板数据显示"""
        if not data:
            return f"\n❌ {user_name} 无看板数据"
        
        result = f"\n🎯 【{user_name}的个性化看板】"
        result += f"\n👤 用户ID: {data['user_id']}"
        result += f"\n⏰ 更新时间: {data['last_updated']}"
        
        # 市场概览
        summary = data['market_summary']
        result += f"\n\n📈 市场概览（基于自选股）:"
        result += f"\n   总股票数: {summary['total_stocks']}"
        result += f"\n   上涨: {summary['up_count']} 只"
        result += f"\n   下跌: {summary['down_count']} 只"
        result += f"\n   平盘: {summary['flat_count']} 只"
        result += f"\n   上涨比例: {summary['up_ratio']}%"
        
        # 自选股行情
        result += f"\n\n💼 自选股行情:"
        if not data['watchlist_stocks']:
            result += "\n   暂无自选股数据"
        else:
            for stock in data['watchlist_stocks']:
                change_symbol = "📈" if stock['change_percent'] > 0 else "📉" if stock['change_percent'] < 0 else "➡️"
                result += f"\n   {change_symbol} {stock['stock_code']} - {stock['stock_name']}"
                result += f"\n      价格: ¥{stock['current_price']:.2f}"
                result += f"   涨跌: {stock['change_amount']:+.2f} ({stock['change_percent']:+.2f}%)"
                result += f"\n      成交量: {stock['volume']:,}   成交额: ¥{stock['amount']:.2f}"
                result += f"\n      行情时间: {stock['quote_time']}"
                result += "\n"
        
        return result
    
    def compare_dashboards(self, user1_data: Dict[str, Any], user2_data: Dict[str, Any], 
                          user1_name: str, user2_name: str) -> str:
        """对比两个用户的看板数据"""
        result = f"\n🔍 【看板个性化对比分析】"
        
        if not user1_data or not user2_data:
            return result + "\n❌ 数据不完整，无法对比"
        
        # 自选股数量对比
        stocks1 = len(user1_data['watchlist_stocks'])
        stocks2 = len(user2_data['watchlist_stocks'])
        result += f"\n📊 自选股数量: {user1_name}({stocks1}) vs {user2_name}({stocks2})"
        
        # 股票代码对比
        codes1 = set(stock['stock_code'] for stock in user1_data['watchlist_stocks'])
        codes2 = set(stock['stock_code'] for stock in user2_data['watchlist_stocks'])
        
        common_stocks = codes1 & codes2  # 交集
        unique_to_user1 = codes1 - codes2  # 只有用户1有的
        unique_to_user2 = codes2 - codes1  # 只有用户2有的
        
        result += f"\n🤝 共同关注股票: {list(common_stocks) if common_stocks else '无'}"
        result += f"\n🔐 {user1_name}独有: {list(unique_to_user1) if unique_to_user1 else '无'}"
        result += f"\n🔐 {user2_name}独有: {list(unique_to_user2) if unique_to_user2 else '无'}"
        
        # 市场概览对比
        summary1 = user1_data['market_summary']
        summary2 = user2_data['market_summary']
        result += f"\n\n📈 上涨比例对比: {user1_name}({summary1['up_ratio']}%) vs {user2_name}({summary2['up_ratio']}%)"
        
        # 个性化程度评估
        if codes1 == codes2:
            result += f"\n⚠️  两用户自选股完全相同，看板数据一致"
        else:
            personalization_score = len(unique_to_user1 | unique_to_user2) / (len(codes1 | codes2) or 1) * 100
            result += f"\n🎯 个性化程度: {personalization_score:.1f}% (差异化股票占比)"
        
        return result

def main():
    """主函数"""
    print("🚀 开始测试看板个性化功能")
    print("="*60)
    
    tester = DashboardTester()
    
    # 测试用户1: admin (已有自选股)
    print("\n1️⃣ 测试用户1: admin")
    token1 = tester.login("admin", "admin123")
    if not token1:
        print("❌ admin用户登录失败，退出测试")
        return
    
    # 获取admin的看板数据
    dashboard1 = tester.get_dashboard_data(token1)
    watchlist1 = tester.get_watchlist(token1)
    
    print(tester.format_dashboard_data(dashboard1, "admin"))
    
    # 尝试测试用户2（如果存在的话）
    print("\n2️⃣ 尝试测试用户2: test")
    token2 = tester.login("test", "test123")
    
    if token2:
        # test用户登录成功
        print("✅ test用户已存在")
        dashboard2 = tester.get_dashboard_data(token2)
        watchlist2 = tester.get_watchlist(token2)
        
        print(tester.format_dashboard_data(dashboard2, "test"))
        
        # 对比两个用户的看板数据
        print(tester.compare_dashboards(dashboard1, dashboard2, "admin", "test"))
        
    else:
        print("⚠️  test用户不存在或密码错误")
        print("💡 建议: 运行以下命令创建test用户:")
        print("   python3 scripts/create_test_user.py")
    
    print("\n" + "="*60)
    print("🎉 看板个性化测试完成!")
    print("\n✨ 总结:")
    print("   - 看板数据根据用户自选股个性化展示")
    print("   - 不同用户看到不同的市场概览统计") 
    print("   - 只显示用户关注的股票行情")
    print("   - API路径: /api/v1/stocks/dashboard")

if __name__ == "__main__":
    main()
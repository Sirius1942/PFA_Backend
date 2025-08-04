#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据更新接口CLI测试脚本
用于手工测试股票数据采集和更新功能
"""

import requests
import json
import sys
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

class DataCollectionCLI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        
    def login(self, username: str, password: str) -> bool:
        """用户登录获取token"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": username,
                    "password": password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                print(f"✅ 登录成功! Token: {self.token[:20] if self.token else 'None'}...")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def collect_stocks_data(self, stock_codes: List[str], include_kline: bool = True, 
                           include_realtime: bool = True, include_info: bool = True) -> Dict[str, Any]:
        """采集指定股票的数据"""
        try:
            payload = {
                "stock_codes": stock_codes,
                "include_kline": include_kline,
                "include_realtime": include_realtime,
                "include_info": include_info
            }
            
            print(f"\n📊 正在发起股票数据采集请求...")
            print(f"📍 股票代码: {', '.join(stock_codes)}")
            print(f"📈 K线数据: {'✅' if include_kline else '❌'}")
            print(f"⚡ 实时行情: {'✅' if include_realtime else '❌'}")
            print(f"ℹ️ 基本信息: {'✅' if include_info else '❌'}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/data/collect/stocks",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 数据采集请求成功提交!")
                print(f"📊 采集状态: {result.get('status')}")
                print(f"💬 消息: {result.get('message')}")
                return result
            else:
                print(f"❌ 数据采集失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ 数据采集异常: {e}")
            return {"error": str(e)}
    
    def collect_realtime_data(self, stock_codes: List[str]) -> Dict[str, Any]:
        """采集实时行情数据"""
        try:
            print(f"\n⚡ 正在采集实时行情数据...")
            print(f"📍 股票代码: {', '.join(stock_codes)}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/data/collect/realtime",
                json=stock_codes
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 实时行情采集请求成功!")
                print(f"📊 采集状态: {result.get('status')}")
                print(f"💬 消息: {result.get('message')}")
                return result
            else:
                print(f"❌ 实时行情采集失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ 实时行情采集异常: {e}")
            return {"error": str(e)}
    
    def update_watchlist_stocks(self) -> Dict[str, Any]:
        """更新自选股数据（调试模式）"""
        try:
            print(f"\n🔄 正在更新自选股数据（调试模式）...")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/data/collect/update-watchlist"
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 自选股数据更新请求成功!")
                print(f"📊 更新状态: {result.get('status')}")
                print(f"💬 消息: {result.get('message')}")
                details = result.get('details', {})
                if 'stock_codes' in details:
                    print(f"📍 更新股票: {', '.join(details['stock_codes'])}")
                return result
            else:
                print(f"❌ 自选股数据更新失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ 自选股数据更新异常: {e}")
            return {"error": str(e)}
    
    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索股票"""
        try:
            print(f"\n🔍 正在搜索股票: '{keyword}'...")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/data/collect/search",
                params={"keyword": keyword, "limit": limit}
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ 搜索完成! 找到 {len(results)} 个结果")
                
                for i, stock in enumerate(results[:5], 1):  # 只显示前5个
                    print(f"  {i}. {stock.get('code', 'N/A')} - {stock.get('name', 'N/A')}")
                
                if len(results) > 5:
                    print(f"  ... 还有 {len(results) - 5} 个结果")
                
                return results
            else:
                print(f"❌ 股票搜索失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 股票搜索异常: {e}")
            return []
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "="*60)
        print("🎯 数据更新接口测试菜单")
        print("="*60)
        print("1. 📊 采集指定股票完整数据")
        print("2. ⚡ 采集指定股票实时行情") 
        print("3. 🔄 更新自选股数据（调试模式）")
        print("4. 🔍 搜索股票")
        print("5. 🎁 采集热门股票数据")
        print("6. 📈 批量采集实时行情")
        print("0. 🚪 退出")
        print("="*60)
    
    def get_stock_codes_input(self, prompt: str = "请输入股票代码") -> List[str]:
        """获取股票代码输入"""
        codes_str = input(f"{prompt} (多个代码用逗号或空格分隔): ").strip()
        if not codes_str:
            return []
        
        # 支持逗号或空格分隔
        if ',' in codes_str:
            codes = [code.strip() for code in codes_str.split(',')]
        else:
            codes = codes_str.split()
        
        # 过滤空值
        codes = [code for code in codes if code]
        return codes
    
    def run_interactive_mode(self):
        """运行交互模式"""
        while True:
            self.show_menu()
            choice = input("请选择操作 (0-6): ").strip()
            
            if choice == "0":
                print("👋 感谢使用数据更新接口测试工具!")
                break
            elif choice == "1":
                # 采集指定股票完整数据
                codes = self.get_stock_codes_input("📊 请输入要采集的股票代码")
                if codes:
                    include_kline = input("是否包含K线数据? (y/N): ").strip().lower() in ['y', 'yes', '是']
                    include_realtime = input("是否包含实时行情? (Y/n): ").strip().lower() not in ['n', 'no', '否']
                    include_info = input("是否包含基本信息? (Y/n): ").strip().lower() not in ['n', 'no', '否']
                    
                    self.collect_stocks_data(codes, include_kline, include_realtime, include_info)
                else:
                    print("❌ 未输入股票代码")
                    
            elif choice == "2":
                # 采集指定股票实时行情
                codes = self.get_stock_codes_input("⚡ 请输入要采集实时行情的股票代码")
                if codes:
                    self.collect_realtime_data(codes)
                else:
                    print("❌ 未输入股票代码")
                    
            elif choice == "3":
                # 更新自选股数据
                confirm = input("🔄 确认更新自选股数据? (Y/n): ").strip().lower()
                if confirm not in ['n', 'no', '否']:
                    self.update_watchlist_stocks()
                    
            elif choice == "4":
                # 搜索股票
                keyword = input("🔍 请输入搜索关键词 (股票代码或名称): ").strip()
                if keyword:
                    limit = input("📝 返回结果数量限制 (默认20): ").strip()
                    limit = int(limit) if limit.isdigit() else 20
                    self.search_stocks(keyword, limit)
                else:
                    print("❌ 未输入搜索关键词")
                    
            elif choice == "5":
                # 采集热门股票数据
                hot_stocks = ["000001", "600519", "300750", "000002", "600036"]
                print(f"🎁 采集热门股票: {', '.join(hot_stocks)}")
                self.collect_stocks_data(hot_stocks, True, True, True)
                
            elif choice == "6":
                # 批量采集实时行情
                batch_stocks = ["000001", "600519", "300750", "000002", "600036", "601166", "600900"]
                print(f"📈 批量采集实时行情: {', '.join(batch_stocks)}")
                self.collect_realtime_data(batch_stocks)
                
            else:
                print("❌ 无效选择，请重新输入")
            
            # 等待用户确认继续
            input("\n按回车键继续...")

def main():
    """主函数"""
    # 固定配置参数 - 调试用
    BASE_URL = "http://localhost:8000"
    USERNAME = "admin"
    PASSWORD = "admin123"
    
    print("🔧 数据更新接口CLI测试工具")
    print(f"📡 服务地址: {BASE_URL}")
    print(f"👤 用户: {USERNAME}")
    print("="*60)
    
    # 创建CLI实例
    cli = DataCollectionCLI(BASE_URL)
    
    # 登录
    print("\n🔐 正在登录...")
    if not cli.login(USERNAME, PASSWORD):
        print("❌ 登录失败，退出程序")
        return
    
    # 运行交互模式
    try:
        cli.run_interactive_mode()
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，程序退出")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自选股管理接口CLI测试脚本
用于手工测试自选股的增删改查功能
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List

class WatchlistCLI:
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
    
    def get_watchlist(self) -> List[Dict[str, Any]]:
        """获取用户自选股列表"""
        try:
            print(f"\n📋 正在获取自选股列表...")
            
            response = self.session.get(f"{self.base_url}/api/v1/stocks/watchlist")
            
            if response.status_code == 200:
                watchlist = response.json()
                print(f"✅ 获取成功! 共 {len(watchlist)} 只自选股")
                
                if watchlist:
                    print("\n📊 当前自选股列表:")
                    print("-" * 80)
                    print(f"{'序号':<4} {'股票代码':<10} {'股票名称':<20} {'添加时间':<20} {'备注':<15}")
                    print("-" * 80)
                    
                    for i, stock in enumerate(watchlist, 1):
                        created_at = stock.get('created_at', '')
                        if created_at:
                            created_at = created_at[:19].replace('T', ' ')
                        notes = stock.get('notes') or ''
                        print(f"{i:<4} {stock.get('stock_code', 'N/A'):<10} {stock.get('stock_name', 'N/A'):<20} {created_at:<20} {notes:<15}")
                    print("-" * 80)
                else:
                    print("📝 暂无自选股")
                
                return watchlist
            else:
                print(f"❌ 获取自选股失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 获取自选股异常: {e}")
            return []
    
    def add_to_watchlist(self, stock_code: str, notes: Optional[str] = None) -> Dict[str, Any]:
        """添加股票到自选股"""
        try:
            print(f"\n➕ 正在添加股票到自选股: {stock_code}")
            
            payload = {"stock_code": stock_code}
            if notes:
                payload["notes"] = notes
            
            response = self.session.post(
                f"{self.base_url}/api/v1/stocks/watchlist",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 添加成功!")
                print(f"📊 股票代码: {result.get('stock_code')}")
                print(f"📝 股票名称: {result.get('stock_name')}")
                if result.get('notes'):
                    print(f"💬 备注: {result.get('notes')}")
                print(f"⏰ 添加时间: {result.get('created_at', '').replace('T', ' ')[:19]}")
                return result
            else:
                print(f"❌ 添加失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ 添加异常: {e}")
            return {"error": str(e)}
    
    def update_watchlist_notes(self, stock_code: str, notes: str) -> Dict[str, Any]:
        """更新自选股备注"""
        try:
            print(f"\n✏️ 正在更新股票备注: {stock_code}")
            
            payload = {"notes": notes}
            
            response = self.session.put(
                f"{self.base_url}/api/v1/stocks/watchlist/{stock_code}",
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 更新成功!")
                print(f"📊 股票代码: {result.get('stock_code')}")
                print(f"📝 股票名称: {result.get('stock_name')}")
                print(f"💬 新备注: {result.get('notes')}")
                return result
            else:
                print(f"❌ 更新失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ 更新异常: {e}")
            return {"error": str(e)}
    
    def remove_from_watchlist(self, stock_code: str) -> Dict[str, Any]:
        """从自选股中移除股票"""
        try:
            print(f"\n🗑️ 正在从自选股中移除: {stock_code}")
            
            response = self.session.delete(
                f"{self.base_url}/api/v1/stocks/watchlist/{stock_code}"
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 移除成功!")
                print(f"💬 {result.get('message', '操作完成')}")
                return result
            else:
                print(f"❌ 移除失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {"error": response.text}
                
        except Exception as e:
            print(f"❌ 移除异常: {e}")
            return {"error": str(e)}
    
    def search_stocks(self, keyword: str) -> List[Dict[str, Any]]:
        """搜索股票（用于添加前查找）"""
        try:
            print(f"\n🔍 正在搜索股票: '{keyword}'...")
            
            response = self.session.get(
                f"{self.base_url}/api/v1/stocks/search",
                params={"q": keyword, "limit": 20}
            )
            
            if response.status_code == 200:
                results = response.json()
                print(f"✅ 搜索完成! 找到 {len(results)} 个结果")
                
                if results:
                    print("\n📊 搜索结果:")
                    print("-" * 60)
                    print(f"{'序号':<4} {'股票代码':<10} {'股票名称':<20} {'市场':<8} {'行业':<15}")
                    print("-" * 60)
                    
                    for i, stock in enumerate(results[:10], 1):  # 只显示前10个
                        market = stock.get('market', 'N/A')
                        industry = stock.get('industry', 'N/A')[:15]  # 限制长度
                        print(f"{i:<4} {stock.get('code', 'N/A'):<10} {stock.get('name', 'N/A'):<20} {market:<8} {industry:<15}")
                    
                    if len(results) > 10:
                        print(f"... 还有 {len(results) - 10} 个结果")
                    print("-" * 60)
                
                return results
            else:
                print(f"❌ 搜索失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ 搜索异常: {e}")
            return []
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """获取个性化看板数据"""
        try:
            print(f"\n📊 正在获取个性化看板数据...")
            
            response = self.session.get(f"{self.base_url}/api/v1/stocks/dashboard")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 获取成功!")
                
                market_summary = data.get('market_summary', {})
                watchlist_stocks = data.get('watchlist_stocks', [])
                
                print(f"\n📈 市场概览 (基于您的自选股):")
                print(f"  📊 关注股票总数: {market_summary.get('total_stocks', 0)}")
                print(f"  📈 上涨: {market_summary.get('up_count', 0)} 只")
                print(f"  📉 下跌: {market_summary.get('down_count', 0)} 只")
                print(f"  ➡️ 平盘: {market_summary.get('flat_count', 0)} 只")
                print(f"  📊 上涨比例: {market_summary.get('up_ratio', 0):.2f}%")
                
                if watchlist_stocks:
                    print(f"\n💼 自选股实时行情:")
                    print("-" * 90)
                    print(f"{'股票代码':<10} {'股票名称':<15} {'当前价格':<10} {'涨跌额':<8} {'涨跌幅':<8} {'成交量':<12}")
                    print("-" * 90)
                    
                    for stock in watchlist_stocks:
                        price = f"¥{stock.get('current_price', 0):.2f}"
                        change_amount = f"{stock.get('change_amount', 0):+.2f}"
                        change_percent = f"{stock.get('change_percent', 0):+.2f}%"
                        volume = f"{stock.get('volume', 0):,}"
                        
                        print(f"{stock.get('stock_code', 'N/A'):<10} {stock.get('stock_name', 'N/A')[:15]:<15} {price:<10} {change_amount:<8} {change_percent:<8} {volume:<12}")
                    print("-" * 90)
                
                return data
            else:
                print(f"❌ 获取看板数据失败: {response.status_code}")
                print(f"📄 错误详情: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ 获取看板数据异常: {e}")
            return {}
    
    def show_menu(self):
        """显示菜单"""
        print("\n" + "="*60)
        print("⭐ 自选股管理接口测试菜单")
        print("="*60)
        print("1. 📋 查看自选股列表")
        print("2. ➕ 添加股票到自选股")
        print("3. ✏️ 更新自选股备注")
        print("4. 🗑️ 移除自选股")
        print("5. 🔍 搜索股票")
        print("6. 📊 查看个性化看板数据")
        print("7. 🎁 批量添加热门股票")
        print("8. 🧹 清空所有自选股")
        print("0. 🚪 退出")
        print("="*60)
    
    def batch_add_popular_stocks(self):
        """批量添加热门股票"""
        popular_stocks = [
            ("000001", "平安银行"),
            ("600519", "贵州茅台"),
            ("300750", "宁德时代"),
            ("000002", "万科A"),
            ("600036", "招商银行")
        ]
        
        print(f"\n🎁 批量添加热门股票...")
        success_count = 0
        
        for code, name in popular_stocks:
            print(f"\n➕ 添加 {code} ({name})...")
            result = self.add_to_watchlist(code, f"热门股票 - {name}")
            if "error" not in result:
                success_count += 1
        
        print(f"\n✅ 批量添加完成! 成功添加 {success_count}/{len(popular_stocks)} 只股票")
    
    def clear_all_watchlist(self):
        """清空所有自选股"""
        watchlist = self.get_watchlist()
        if not watchlist:
            print("📝 自选股列表已经为空")
            return
        
        confirm = input(f"\n⚠️ 确认要清空所有 {len(watchlist)} 只自选股吗? (输入 'yes' 确认): ").strip()
        if confirm.lower() != 'yes':
            print("❌ 操作已取消")
            return
        
        print(f"\n🧹 开始清空自选股...")
        success_count = 0
        
        for stock in watchlist:
            stock_code = stock.get('stock_code')
            if stock_code:
                print(f"🗑️ 移除 {stock_code}...")
                result = self.remove_from_watchlist(stock_code)
                if "error" not in result:
                    success_count += 1
        
        print(f"\n✅ 清空完成! 成功移除 {success_count}/{len(watchlist)} 只股票")
    
    def run_interactive_mode(self):
        """运行交互模式"""
        while True:
            self.show_menu()
            choice = input("请选择操作 (0-8): ").strip()
            
            if choice == "0":
                print("👋 感谢使用自选股管理测试工具!")
                break
            elif choice == "1":
                # 查看自选股列表
                self.get_watchlist()
                
            elif choice == "2":
                # 添加股票到自选股
                stock_code = input("📊 请输入股票代码: ").strip().upper()
                if stock_code:
                    notes = input("💬 请输入备注 (可选): ").strip()
                    notes = notes if notes else None
                    self.add_to_watchlist(stock_code, notes)
                else:
                    print("❌ 未输入股票代码")
                    
            elif choice == "3":
                # 更新自选股备注
                stock_code = input("📊 请输入要更新的股票代码: ").strip().upper()
                if stock_code:
                    notes = input("💬 请输入新的备注: ").strip()
                    self.update_watchlist_notes(stock_code, notes)
                else:
                    print("❌ 未输入股票代码")
                    
            elif choice == "4":
                # 移除自选股
                stock_code = input("📊 请输入要移除的股票代码: ").strip().upper()
                if stock_code:
                    confirm = input(f"⚠️ 确认要移除 {stock_code} 吗? (y/N): ").strip().lower()
                    if confirm in ['y', 'yes', '是']:
                        self.remove_from_watchlist(stock_code)
                    else:
                        print("❌ 操作已取消")
                else:
                    print("❌ 未输入股票代码")
                    
            elif choice == "5":
                # 搜索股票
                keyword = input("🔍 请输入搜索关键词 (股票代码或名称): ").strip()
                if keyword:
                    results = self.search_stocks(keyword)
                    if results:
                        add_choice = input("\n➕ 是否要添加其中某只股票到自选股? (y/N): ").strip().lower()
                        if add_choice in ['y', 'yes', '是']:
                            code_input = input("📊 请输入要添加的股票代码: ").strip().upper()
                            if code_input:
                                notes = input("💬 请输入备注 (可选): ").strip()
                                notes = notes if notes else None
                                self.add_to_watchlist(code_input, notes)
                else:
                    print("❌ 未输入搜索关键词")
                    
            elif choice == "6":
                # 查看个性化看板数据
                self.get_dashboard_data()
                
            elif choice == "7":
                # 批量添加热门股票
                confirm = input("🎁 确认要批量添加热门股票吗? (Y/n): ").strip().lower()
                if confirm not in ['n', 'no', '否']:
                    self.batch_add_popular_stocks()
                    
            elif choice == "8":
                # 清空所有自选股
                self.clear_all_watchlist()
                
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
    
    print("⭐ 自选股管理接口CLI测试工具")
    print(f"📡 服务地址: {BASE_URL}")
    print(f"👤 用户: {USERNAME}")
    print("="*60)
    
    # 创建CLI实例
    cli = WatchlistCLI(BASE_URL)
    
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
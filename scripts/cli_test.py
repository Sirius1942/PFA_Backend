#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手接口CLI测试脚本
用于手工测试AI助手的各种功能
"""

import requests
import json
import sys
from datetime import datetime
from typing import Optional, Dict, Any

class AIAssistantCLI:
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
                }
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
                print(f"✅ 登录成功! Token: {self.token[:20]}...")
                return True
            else:
                print(f"❌ 登录失败: {response.text}")
                return False
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return False
    
    def chat(self, message: str, context: Optional[Dict] = None, stock_code: Optional[str] = None) -> Dict[str, Any]:
        """与AI助手对话"""
        try:
            payload = {
                "message": message,
                "context": context or {},
                "stock_code": stock_code
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/assistant/chat",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 聊天请求失败: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"❌ 聊天异常: {e}")
            return {}
    
    def analyze_stock(self, stock_code: str, analysis_type: str = "comprehensive", period: str = "1d", days: int = 30) -> Dict[str, Any]:
        """股票分析"""
        try:
            payload = {
                "stock_code": stock_code,
                "analysis_type": analysis_type,
                "period": period,
                "days": days
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/assistant/analyze-stock",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 股票分析失败: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"❌ 股票分析异常: {e}")
            return {}
    
    def get_market_insights(self, market: Optional[str] = None, industry: Optional[str] = None, insight_type: str = "overview") -> Dict[str, Any]:
        """获取市场洞察"""
        try:
            payload = {
                "market": market,
                "industry": industry,
                "insight_type": insight_type
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/assistant/market-insights",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 市场洞察失败: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"❌ 市场洞察异常: {e}")
            return {}
    
    def get_suggestions(self) -> Dict[str, Any]:
        """获取智能建议"""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/assistant/suggestions"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ 获取建议失败: {response.status_code} - {response.text}")
                return {}
        except Exception as e:
            print(f"❌ 获取建议异常: {e}")
            return {}
    
    def print_response(self, response: Dict[str, Any], title: str = "响应结果"):
        """格式化打印响应结果"""
        print(f"\n{'='*50}")
        print(f"📋 {title}")
        print(f"{'='*50}")
        print(json.dumps(response, ensure_ascii=False, indent=2))
        print(f"{'='*50}\n")

def main():
    # 固定配置参数 - 调试用
    BASE_URL = "http://localhost:8000"
    USERNAME = "admin"
    PASSWORD = "admin123"
    
    print("🔧 AI助手CLI调试工具")
    print(f"📡 服务地址: {BASE_URL}")
    print(f"👤 用户: {USERNAME}")
    print("="*50)
    
    # 创建CLI实例
    cli = AIAssistantCLI(BASE_URL)
    
    # 登录
    print("\n🔐 正在登录...")
    if not cli.login(USERNAME, PASSWORD):
        print("❌ 登录失败，退出程序")
        return
    
    # 显示菜单
    while True:
        print("\n" + "="*50)
        print("🎯 请选择测试功能:")
        print("1. 💬 AI聊天测试")
        print("2. 📈 股票分析测试")
        print("3. 🌍 市场洞察测试")
        print("4. 💡 智能建议测试")
        print("5. 🤖 交互聊天模式")
        print("0. 🚪 退出")
        print("="*50)
        
        try:
            choice = input("\n请输入选项 (0-5): ").strip()
            
            if choice == "0":
                print("👋 再见!")
                break
                
            elif choice == "1":
                # AI聊天测试
                message = input("\n💬 请输入聊天消息: ").strip()
                if message:
                    print("\n🔄 正在请求AI助手...")
                    response = cli.chat(message)
                    cli.print_response(response, "AI助手回复")
                    
            elif choice == "2":
                # 股票分析测试
                stock_code = input("\n📈 请输入股票代码 (如: 000001): ").strip()
                if stock_code:
                    print(f"\n🔄 正在分析股票 {stock_code}...")
                    response = cli.analyze_stock(stock_code, "comprehensive")
                    cli.print_response(response, f"股票分析 - {stock_code}")
                    
            elif choice == "3":
                # 市场洞察测试
                print("\n🔄 正在获取市场洞察...")
                response = cli.get_market_insights()
                cli.print_response(response, "市场洞察")
                
            elif choice == "4":
                # 智能建议测试
                print("\n🔄 正在获取智能建议...")
                response = cli.get_suggestions()
                cli.print_response(response, "智能建议")
                
            elif choice == "5":
                # 交互聊天模式
                print("\n🤖 进入交互聊天模式，输入 'quit' 或 'back' 返回菜单")
                print("-" * 50)
                while True:
                    try:
                        message = input("\n💬 您: ").strip()
                        if message.lower() in ['quit', 'exit', '退出', 'back', '返回']:
                            print("🔙 返回主菜单")
                            break
                        if not message:
                            continue
                            
                        response = cli.chat(message)
                        if response:
                            print(f"\n🤖 AI助手: {response.get('message', '无响应')}")
                            if response.get('suggestions'):
                                print(f"💡 建议: {', '.join(response['suggestions'])}")
                                
                    except KeyboardInterrupt:
                        print("\n🔙 返回主菜单")
                        break
                    except Exception as e:
                        print(f"❌ 错误: {e}")
                        
            else:
                print("❌ 无效选项，请重新选择")
                
        except KeyboardInterrupt:
            print("\n👋 再见!")
            break
        except Exception as e:
            print(f"❌ 程序错误: {e}")
            continue

if __name__ == "__main__":
    main()
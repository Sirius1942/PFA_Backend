#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手接口CLI测试脚本
用于手工测试AI助手的各种功能
"""

import requests
import json
import sys
import argparse
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
    parser = argparse.ArgumentParser(description="AI助手CLI测试工具")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务地址")
    parser.add_argument("--username", default="admin", help="用户名")
    parser.add_argument("--password", default="admin123", help="密码")
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # 聊天命令
    chat_parser = subparsers.add_parser("chat", help="与AI助手对话")
    chat_parser.add_argument("message", help="聊天消息")
    chat_parser.add_argument("--stock", help="股票代码")
    
    # 股票分析命令
    stock_parser = subparsers.add_parser("stock", help="股票分析")
    stock_parser.add_argument("code", help="股票代码")
    stock_parser.add_argument("--type", default="comprehensive", choices=["technical", "fundamental", "comprehensive"], help="分析类型")
    stock_parser.add_argument("--period", default="1d", help="K线周期")
    stock_parser.add_argument("--days", type=int, default=30, help="分析天数")
    
    # 市场洞察命令
    market_parser = subparsers.add_parser("market", help="市场洞察")
    market_parser.add_argument("--market", choices=["SH", "SZ", "BJ"], help="市场")
    market_parser.add_argument("--industry", help="行业")
    market_parser.add_argument("--type", default="overview", choices=["overview", "trend", "hotspots"], help="洞察类型")
    
    # 建议命令
    subparsers.add_parser("suggestions", help="获取智能建议")
    
    # 交互模式
    subparsers.add_parser("interactive", help="交互模式")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # 创建CLI实例
    cli = AIAssistantCLI(args.url)
    
    # 登录
    if not cli.login(args.username, args.password):
        return
    
    # 执行命令
    if args.command == "chat":
        response = cli.chat(args.message, stock_code=args.stock)
        cli.print_response(response, "AI助手回复")
        
    elif args.command == "stock":
        response = cli.analyze_stock(args.code, args.type, args.period, args.days)
        cli.print_response(response, f"股票分析 - {args.code}")
        
    elif args.command == "market":
        response = cli.get_market_insights(args.market, args.industry, args.type)
        cli.print_response(response, "市场洞察")
        
    elif args.command == "suggestions":
        response = cli.get_suggestions()
        cli.print_response(response, "智能建议")
        
    elif args.command == "interactive":
        print("🤖 进入交互模式，输入 'quit' 退出")
        while True:
            try:
                message = input("\n💬 您: ").strip()
                if message.lower() in ['quit', 'exit', '退出']:
                    print("👋 再见!")
                    break
                if not message:
                    continue
                    
                response = cli.chat(message)
                if response:
                    print(f"\n🤖 AI助手: {response.get('message', '无响应')}")
                    if response.get('suggestions'):
                        print(f"💡 建议: {', '.join(response['suggestions'])}")
                        
            except KeyboardInterrupt:
                print("\n👋 再见!")
                break
            except Exception as e:
                print(f"❌ 错误: {e}")

if __name__ == "__main__":
    main()
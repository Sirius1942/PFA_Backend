#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Token使用示例脚本
演示如何在实际项目中集成admin登录和token使用
"""

import requests
import json
from typing import Optional, Dict, Any
from get_token import get_admin_token

class AuthenticatedAPIClient:
    """带认证的API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def authenticate(self, username: str = "admin", password: str = "admin123") -> bool:
        """认证并获取token"""
        print(f"🔐 正在认证用户: {username}")
        
        self.token = get_admin_token(self.base_url, username, password, quiet=True)
        
        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            })
            print(f"✅ 认证成功，token已设置")
            return True
        else:
            print(f"❌ 认证失败")
            return False
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.token is not None
    
    def chat_with_ai(self, message: str, stock_code: Optional[str] = None) -> Dict[str, Any]:
        """与AI助手聊天"""
        if not self.is_authenticated():
            return {"error": "未认证，请先调用authenticate()"}
        
        payload = {
            "message": message,
            "context": {},
            "stock_code": stock_code
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/assistant/chat",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"请求失败: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"请求异常: {e}"}
    
    def get_suggestions(self) -> Dict[str, Any]:
        """获取智能建议"""
        if not self.is_authenticated():
            return {"error": "未认证，请先调用authenticate()"}
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/assistant/suggestions"
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"请求失败: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"请求异常: {e}"}
    
    def analyze_stock(self, stock_code: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """分析股票"""
        if not self.is_authenticated():
            return {"error": "未认证，请先调用authenticate()"}
        
        payload = {
            "stock_code": stock_code,
            "analysis_type": analysis_type,
            "period": "1d",
            "days": 30
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/assistant/analyze-stock",
                json=payload
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"请求失败: {response.status_code} - {response.text}"}
                
        except Exception as e:
            return {"error": f"请求异常: {e}"}

def demo_basic_usage():
    """基础使用演示"""
    print("\n" + "="*50)
    print("🚀 基础使用演示")
    print("="*50)
    
    # 创建客户端
    client = AuthenticatedAPIClient()
    
    # 认证
    if not client.authenticate():
        print("❌ 认证失败，无法继续演示")
        return
    
    # 测试聊天
    print("\n💬 测试AI聊天:")
    chat_result = client.chat_with_ai("你好，我想了解一下股票投资的基本知识")
    if "error" not in chat_result:
        print(f"🤖 AI回复: {chat_result.get('message', '无回复')[:100]}...")
    else:
        print(f"❌ 聊天失败: {chat_result['error']}")
    
    # 测试建议
    print("\n💡 测试智能建议:")
    suggestions_result = client.get_suggestions()
    if "error" not in suggestions_result:
        print(f"✅ 建议获取成功")
    else:
        print(f"❌ 建议获取失败: {suggestions_result['error']}")

def demo_advanced_usage():
    """高级使用演示"""
    print("\n" + "="*50)
    print("🔧 高级使用演示")
    print("="*50)
    
    # 直接使用token
    print("\n🎫 直接获取和使用token:")
    token = get_admin_token(quiet=True)
    if token:
        print(f"✅ Token获取成功: {token[:30]}...")
        
        # 手动构造请求
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {"message": "请简单介绍一下技术分析"}
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/assistant/chat",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"🤖 手动请求成功: {data.get('message', '无回复')[:100]}...")
            else:
                print(f"❌ 手动请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 手动请求异常: {e}")
    else:
        print("❌ Token获取失败")

def demo_error_handling():
    """错误处理演示"""
    print("\n" + "="*50)
    print("🛠️ 错误处理演示")
    print("="*50)
    
    # 测试未认证的请求
    print("\n🚫 测试未认证请求:")
    client = AuthenticatedAPIClient()
    result = client.chat_with_ai("测试消息")
    print(f"预期错误: {result.get('error', '无错误')}")
    
    # 测试错误的认证信息
    print("\n🔐 测试错误认证:")
    client2 = AuthenticatedAPIClient()
    auth_result = client2.authenticate("wrong_user", "wrong_pass")
    print(f"认证结果: {'成功' if auth_result else '失败（预期）'}")

def main():
    """主函数"""
    print("🎯 Token使用示例演示")
    print("展示如何在实际项目中集成admin登录和API调用")
    
    # 基础使用
    demo_basic_usage()
    
    # 高级使用
    demo_advanced_usage()
    
    # 错误处理
    demo_error_handling()
    
    print("\n" + "="*50)
    print("📚 集成指南")
    print("="*50)
    print("\n1. 在你的项目中导入:")
    print("   from token_usage_example import AuthenticatedAPIClient")
    print("\n2. 创建客户端并认证:")
    print("   client = AuthenticatedAPIClient()")
    print("   client.authenticate()")
    print("\n3. 调用API:")
    print("   result = client.chat_with_ai('你的消息')")
    print("\n4. 或直接获取token:")
    print("   from get_token import get_admin_token")
    print("   token = get_admin_token(quiet=True)")
    
    print("\n✅ 演示完成！")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Admin登录权限测试脚本
演示如何使用admin账号登录获取token并调用AI助手接口
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any, Optional

class AdminTokenManager:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None
        self.user_info = None
        
    def login_as_admin(self, username: str = "admin", password: str = "admin123") -> Dict[str, Any]:
        """使用admin账号登录获取权限token"""
        print(f"🔐 正在使用admin账号登录...")
        print(f"   用户名: {username}")
        print(f"   密码: {'*' * len(password)}")
        print(f"   服务地址: {self.base_url}")
        
        try:
            # 发送登录请求
            login_data = {
                "username": username,
                "password": password
            }
            
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data=login_data
            )
            
            print(f"\n📡 登录请求状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.user_info = data.get("user")
                
                # 设置认证头
                self.session.headers.update({
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                })
                
                print(f"✅ 登录成功!")
                print(f"🎫 Token: {self.token[:30]}...")
                print(f"👤 用户信息: {json.dumps(self.user_info, ensure_ascii=False, indent=2) if self.user_info else '未返回'}")
                
                return {
                    "success": True,
                    "token": self.token,
                    "user_info": self.user_info,
                    "message": "登录成功"
                }
            else:
                error_msg = response.text
                print(f"❌ 登录失败: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "message": "登录失败"
                }
                
        except Exception as e:
            print(f"❌ 登录异常: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "登录异常"
            }
    
    def test_token_validity(self) -> bool:
        """测试token有效性"""
        if not self.token:
            print("❌ 没有可用的token")
            return False
            
        try:
            # 尝试访问需要认证的接口
            response = self.session.get(f"{self.base_url}/api/v1/assistant/suggestions")
            
            print(f"\n🔍 Token验证请求状态: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Token有效，具有访问权限")
                return True
            elif response.status_code == 401:
                print("❌ Token无效或已过期")
                return False
            else:
                print(f"⚠️  未知状态: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Token验证异常: {e}")
            return False
    
    def call_ai_chat(self, message: str) -> Dict[str, Any]:
        """调用AI聊天接口"""
        if not self.token:
            return {"error": "未登录，请先获取token"}
            
        try:
            payload = {
                "message": message,
                "context": {},
                "stock_code": None
            }
            
            print(f"\n💬 发送聊天消息: {message}")
            
            response = self.session.post(
                f"{self.base_url}/api/v1/assistant/chat",
                json=payload
            )
            
            print(f"📡 聊天请求状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ AI回复成功")
                return data
            else:
                error_msg = response.text
                print(f"❌ AI回复失败: {error_msg}")
                return {"error": error_msg}
                
        except Exception as e:
            print(f"❌ 聊天异常: {e}")
            return {"error": str(e)}
    
    def get_user_permissions(self) -> Dict[str, Any]:
        """获取用户权限信息"""
        if not self.token:
            return {"error": "未登录，请先获取token"}
            
        try:
            # 尝试获取用户信息
            response = self.session.get(f"{self.base_url}/api/v1/users/me")
            
            print(f"\n👤 获取用户信息状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 用户权限信息获取成功")
                return data
            else:
                error_msg = response.text
                print(f"❌ 获取用户信息失败: {error_msg}")
                return {"error": error_msg}
                
        except Exception as e:
            print(f"❌ 获取用户信息异常: {e}")
            return {"error": str(e)}
    
    def demonstrate_admin_capabilities(self):
        """演示admin权限的各种功能"""
        print("\n" + "="*60)
        print("🚀 Admin权限功能演示")
        print("="*60)
        
        # 1. 登录获取token
        login_result = self.login_as_admin()
        if not login_result["success"]:
            print("❌ 登录失败，无法继续演示")
            return
        
        # 2. 验证token有效性
        print("\n" + "-"*40)
        print("🔍 验证Token有效性")
        print("-"*40)
        self.test_token_validity()
        
        # 3. 获取用户权限信息
        print("\n" + "-"*40)
        print("👤 获取用户权限信息")
        print("-"*40)
        user_info = self.get_user_permissions()
        if "error" not in user_info:
            print(f"📋 权限详情: {json.dumps(user_info, ensure_ascii=False, indent=2)}")
        
        # 4. 测试AI聊天功能
        print("\n" + "-"*40)
        print("🤖 测试AI聊天功能")
        print("-"*40)
        chat_result = self.call_ai_chat("你好，我是管理员，请介绍你的功能")
        if "error" not in chat_result:
            print(f"🤖 AI回复: {chat_result.get('message', '无回复')}")
        
        # 5. 显示token信息
        print("\n" + "-"*40)
        print("🎫 Token信息总结")
        print("-"*40)
        print(f"Token: {self.token}")
        print(f"Token长度: {len(self.token) if self.token else 0}")
        print(f"认证头: Authorization: Bearer {self.token[:20]}..." if self.token else "无认证头")
        
        print("\n" + "="*60)
        print("✅ Admin权限演示完成")
        print("="*60)

def main():
    """主函数"""
    print("🔐 Admin登录权限测试工具")
    print("="*50)
    
    # 创建token管理器
    admin_manager = AdminTokenManager()
    
    # 演示完整的admin功能
    admin_manager.demonstrate_admin_capabilities()
    
    print("\n💡 使用说明:")
    print("1. 此脚本演示了如何使用admin账号登录获取token")
    print("2. Token可用于调用所有需要认证的API接口")
    print("3. 可以复制token用于其他工具或脚本")
    print("4. Token格式: Bearer <token_string>")
    print("\n🔧 集成到其他脚本:")
    print("```python")
    print("from admin_login_test import AdminTokenManager")
    print("manager = AdminTokenManager()")
    print("result = manager.login_as_admin()")
    print("token = result['token'] if result['success'] else None")
    print("```")

if __name__ == "__main__":
    main()
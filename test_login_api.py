#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
登录接口测试脚本
测试admin账户登录功能是否正常
"""

import requests
import json
from datetime import datetime

def test_login_api():
    """测试登录API"""
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    # 测试数据
    test_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    print(f"[{datetime.now()}] 开始测试登录接口...")
    print(f"登录URL: {login_url}")
    print(f"测试账户: {test_credentials['username']}")
    print("-" * 50)
    
    try:
        # 发送登录请求 - 使用form-data格式
        response = requests.post(
            login_url,
            data=test_credentials,  # 使用data而不是json
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                response_data = response.json()
                print("✅ 登录成功!")
                print(f"响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # 检查响应数据结构
                if "access_token" in response_data:
                    print("✅ 包含访问令牌")
                    token = response_data["access_token"]
                    print(f"令牌长度: {len(token)}")
                    
                    # 测试使用令牌访问受保护的接口
                    test_protected_api(base_url, token)
                else:
                    print("⚠️ 响应中未找到access_token")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
                print(f"原始响应: {response.text}")
        else:
            print(f"❌ 登录失败，状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 连接失败: 无法连接到后端服务")
        print("请确保后端服务正在运行在 http://localhost:8000")
    except requests.exceptions.Timeout:
        print("❌ 请求超时")
    except Exception as e:
        print(f"❌ 请求异常: {e}")

def test_protected_api(base_url, token):
    """测试受保护的API接口"""
    print("\n" + "-" * 30)
    print("测试受保护的API接口...")
    
    # 测试获取用户信息接口
    user_info_url = f"{base_url}/api/v1/auth/profile"
    
    try:
        response = requests.get(
            user_info_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        
        print(f"用户信息接口状态码: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ 获取用户信息成功!")
            print(f"用户信息: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
            
    except Exception as e:
        print(f"❌ 测试受保护API异常: {e}")

def test_valid_credentials():
    """测试正确的登录凭据"""
    print("\n" + "=" * 50)
    print("测试正确的登录凭据...")
    
    base_url = "http://localhost:8000"
    login_url = f"{base_url}/api/v1/auth/login"
    
    # 正确的凭据
    valid_credentials = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(
            login_url,
            data=valid_credentials,  # 使用data而不是json
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        print(f"正确凭据响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 正确凭据登录成功")
            try:
                response_data = response.json()
                print(f"登录响应数据: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                if "access_token" in response_data:
                    print("✅ 成功获取访问令牌")
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析失败: {e}")
        else:
            print(f"⚠️ 意外的响应状态码: {response.status_code}")
            
        print(f"响应内容: {response.text}")
        
    except Exception as e:
        print(f"❌ 测试正确凭据异常: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("私人金融分析师 - 登录接口测试")
    print("=" * 60)
    
    # 测试正确的登录凭据
    test_login_api()
    
    # 测试正确的登录凭据（第二次验证）
    test_valid_credentials()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
私人金融分析师系统测试脚本
测试数据库连接、后端API和登录功能
"""

import requests
import pymysql
import json
from datetime import datetime
import sys
import os

def test_database_connection():
    """测试数据库连接"""
    print("🔍 测试数据库连接...")
    try:
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            database='financial_db',
            user='financial_user',
            password='financial123'
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        
        print(f"✅ 数据库连接成功! 测试结果: {result}")
        
        # 检查用户表
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"📊 数据库中用户数量: {user_count}")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def test_backend_health():
    """测试后端健康状况"""
    print("\n🔍 测试后端健康状况...")
    try:
        # 测试根路径
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"✅ 根路径访问成功: {response.status_code}")
        
        # 测试健康检查
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ 健康检查成功: {response.status_code}")
        
        # 测试API文档
        response = requests.get("http://localhost:8000/docs", timeout=5)
        print(f"✅ API文档访问成功: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return False

def test_login_api():
    """测试登录API"""
    print("\n🔍 测试登录API...")
    
    # 测试用户登录
    test_users = [
        {"username": "admin", "password": "admin123", "name": "管理员"},
        {"username": "test", "password": "test123", "name": "测试用户"}
    ]
    
    successful_logins = 0
    
    for user in test_users:
        try:
            login_data = {
                "username": user["username"],
                "password": user["password"]
            }
            
            response = requests.post(
                "http://localhost:8000/api/v1/auth/login",
                data=login_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=5
            )
            
            if response.status_code == 200:
                token_data = response.json()
                print(f"✅ {user['name']}登录成功")
                print(f"   - Access Token: {token_data['access_token'][:50]}...")
                print(f"   - Token Type: {token_data['token_type']}")
                successful_logins += 1
                
                # 测试使用token获取用户信息
                headers = {"Authorization": f"Bearer {token_data['access_token']}"}
                profile_response = requests.get(
                    "http://localhost:8000/api/v1/auth/profile",
                    headers=headers,
                    timeout=5
                )
                
                if profile_response.status_code == 200:
                    profile = profile_response.json()
                    print(f"   - 用户信息获取成功: {profile['username']} ({profile['email']})")
                else:
                    print(f"   - ⚠️ 用户信息获取失败: {profile_response.status_code}")
                    
            else:
                print(f"❌ {user['name']}登录失败: {response.status_code}")
                print(f"   响应内容: {response.text}")
                
        except Exception as e:
            print(f"❌ {user['name']}登录测试异常: {e}")
    
    return successful_logins == len(test_users)

def test_frontend_connection():
    """测试前端连接"""
    print("\n🔍 测试前端连接...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ 前端访问成功")
            return True
        else:
            print(f"⚠️ 前端访问异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 前端连接失败: {e}")
        print("💡 前端可能未启动或启动失败")
        return False

def main():
    """主测试函数"""
    print("🚀 开始私人金融分析师系统全面测试")
    print("=" * 50)
    
    tests = [
        ("数据库连接", test_database_connection),
        ("后端健康", test_backend_health),
        ("登录API", test_login_api),
        ("前端连接", test_frontend_connection)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        results[test_name] = test_func()
    
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    
    success_count = 0
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            success_count += 1
    
    print(f"\n📈 总体结果: {success_count}/{len(tests)} 项测试通过")
    
    if success_count == len(tests):
        print("🎉 所有测试通过！系统运行正常！")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查相关组件")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 
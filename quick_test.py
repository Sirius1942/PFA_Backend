#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 无需认证的简单测试
"""

import requests
import json

def test_health():
    """测试健康检查接口"""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"🏥 健康检查: {response.status_code}")
        print(f"📋 响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def test_root():
    """测试根接口"""
    try:
        response = requests.get("http://localhost:8000/")
        print(f"🏠 根接口: {response.status_code}")
        print(f"📋 响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 根接口测试失败: {e}")
        return False

def test_docs():
    """测试API文档接口"""
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"📚 API文档: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API文档测试失败: {e}")
        return False

def test_chat_without_auth():
    """测试聊天接口（无认证）"""
    try:
        payload = {
            "message": "你好，请介绍一下你的功能"
        }
        response = requests.post(
            "http://localhost:8000/api/v1/assistant/chat",
            json=payload
        )
        print(f"💬 聊天接口: {response.status_code}")
        if response.status_code == 401:
            print("🔒 需要认证（正常）")
        else:
            print(f"📋 响应: {response.text}")
        return True
    except Exception as e:
        print(f"❌ 聊天接口测试失败: {e}")
        return False

def main():
    print("🚀 开始快速测试...")
    print("="*50)
    
    tests = [
        ("健康检查", test_health),
        ("根接口", test_root),
        ("API文档", test_docs),
        ("聊天接口", test_chat_without_auth)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n🧪 测试: {name}")
        print("-" * 30)
        result = test_func()
        results.append((name, result))
        print(f"结果: {'✅ 通过' if result else '❌ 失败'}")
    
    print("\n" + "="*50)
    print("📊 测试总结:")
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    print(f"\n🎯 通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if all(result for _, result in results):
        print("\n🎉 所有测试通过！服务运行正常")
        print("\n💡 使用说明:")
        print("  1. API文档: http://localhost:8000/docs")
        print("  2. 完整测试: python cli_test.py interactive")
        print("  3. 聊天测试: python cli_test.py chat '你好'")
        print("  4. 股票分析: python cli_test.py stock 000001")
    else:
        print("\n⚠️  部分测试失败，请检查服务状态")

if __name__ == "__main__":
    main()
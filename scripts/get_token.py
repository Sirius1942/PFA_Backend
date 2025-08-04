#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速获取Admin Token工具
用于快速获取认证token，方便在其他工具中使用
"""

import requests
import sys
import argparse

def get_admin_token(base_url="http://localhost:8000", username="admin", password="admin123", quiet=False):
    """获取admin token"""
    try:
        if not quiet:
            print(f"🔐 正在获取admin token...")
            
        response = requests.post(
            f"{base_url}/api/v1/auth/login",
            data={
                "username": username,
                "password": password
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            
            if not quiet:
                print(f"✅ 获取成功!")
                print(f"🎫 Token: {token}")
                print(f"\n📋 使用方法:")
                print(f"   curl -H \"Authorization: Bearer {token}\" ...")
                print(f"   或在Python中: headers = {{'Authorization': 'Bearer {token}'}}")
            else:
                print(token)
                
            return token
        else:
            if not quiet:
                print(f"❌ 获取失败: {response.text}")
            return None
            
    except Exception as e:
        if not quiet:
            print(f"❌ 异常: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="快速获取Admin Token")
    parser.add_argument("--url", default="http://localhost:8000", help="API服务地址")
    parser.add_argument("--username", default="admin", help="用户名")
    parser.add_argument("--password", default="admin123", help="密码")
    parser.add_argument("--quiet", "-q", action="store_true", help="静默模式，只输出token")
    parser.add_argument("--export", "-e", action="store_true", help="输出export命令格式")
    
    args = parser.parse_args()
    
    token = get_admin_token(args.url, args.username, args.password, args.quiet)
    
    if token and args.export:
        print(f"export AUTH_TOKEN='{token}'")
        print(f"# 使用: curl -H \"Authorization: Bearer $AUTH_TOKEN\" ...")
    
    return 0 if token else 1

if __name__ == "__main__":
    sys.exit(main())
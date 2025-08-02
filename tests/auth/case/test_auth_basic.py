#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模块基本测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestAuthBasic(APITestCase):
    """基本认证功能测试"""
    
    def test_admin_login_success(self):
        """测试管理员登录成功"""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # 验证响应包含必要字段
        self.assertIn("access_token", response_data)
        self.assertIn("token_type", response_data)
        self.assertEqual(response_data["token_type"], "bearer")
        
        # 验证token长度合理
        self.assertGreater(len(response_data["access_token"]), 50)
    
    def test_get_user_profile(self):
        """测试获取用户资料"""
        response = self.make_request('GET', '/api/v1/auth/profile')
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # 验证用户资料字段
        expected_fields = self.test_data.get("profile_test_data", {}).get("expected_fields", [])
        for field in expected_fields:
            self.assertIn(field, response_data)
        
        # 验证用户是admin
        self.assertEqual(response_data.get("username"), "admin")
    
    def test_token_authentication(self):
        """测试token认证流程"""
        # 1. 登录获取token
        login_response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        self.assertEqual(login_response.status_code, 200)
        token = login_response.json()["access_token"]
        
        # 2. 使用token访问受保护资源
        headers = {"Authorization": f"Bearer {token}"}
        profile_response = self.session.get(
            f"{self.base_url}/api/v1/auth/profile",
            headers=headers
        )
        
        self.assertEqual(profile_response.status_code, 200)
        profile_data = profile_response.json()
        self.assertEqual(profile_data.get("username"), "admin")


if __name__ == '__main__':
    unittest.main()

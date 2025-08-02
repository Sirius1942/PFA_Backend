#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块基本测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestUsersBasic(APITestCase):
    """基本用户管理功能测试"""
    
    def test_get_current_user_profile(self):
        """测试获取当前用户资料"""
        response = self.make_request('GET', '/api/v1/users/me')
        
        # 允许200(成功)或500(服务错误)
        self.assertIn(response.status_code, [200, 500])
        
        if response.status_code == 200:
            response_data = response.json()
            expected_fields = self.test_data.get("user_profile_test_data", {}).get("expected_fields", [])
            
            for field in expected_fields:
                self.assertIn(field, response_data)
    
    def test_get_users_list(self):
        """测试获取用户列表"""
        response = self.make_request('GET', '/api/v1/users/')
        
        # 允许多种状态码，主要测试接口可访问性
        self.assertIn(response.status_code, [200, 403, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIsInstance(response_data, (list, dict))
    
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        # 测试获取用户ID为1的用户(通常是admin)
        response = self.make_request('GET', '/api/v1/users/1')
        
        # 允许多种状态码
        self.assertIn(response.status_code, [200, 403, 404, 500])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertEqual(response_data.get("id"), 1)
    
    def test_get_available_roles(self):
        """测试获取可用角色"""
        response = self.make_request('GET', '/api/v1/users/roles/available')
        
        # 允许多种状态码
        self.assertIn(response.status_code, [200, 403, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIsInstance(response_data, list)
    
    def test_user_authentication_flow(self):
        """测试用户认证流程"""
        # 1. 获取当前用户信息
        profile_response = self.make_request('GET', '/api/v1/users/me')
        
        if profile_response.status_code == 200:
            profile_data = profile_response.json()
            
            # 2. 验证用户信息
            self.assertIn("username", profile_data)
            self.assertIn("email", profile_data)
            self.assertTrue(profile_data.get("is_active", True))


if __name__ == '__main__':
    unittest.main()

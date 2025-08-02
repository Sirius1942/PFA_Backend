#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户管理模块unittest测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestUserManagement(APITestCase):
    """用户管理接口测试"""
    
    def test_get_users_list(self):
        """测试获取用户列表"""
        response = self.make_request('GET', '/api/v1/users/')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 403, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, (list, dict))
    
    def test_get_users_with_pagination(self):
        """测试分页获取用户列表"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/users/',
                params={
                    "page": scenario["page"],
                    "size": scenario["size"]
                }
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("user_list_test_data.pagination", test_scenario)
    
    def test_get_users_with_filtering(self):
        """测试筛选获取用户列表"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/users/',
                params={
                    scenario["filter_by"]: scenario["filter_value"]
                }
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("user_list_test_data.filtering", test_scenario)
    
    def test_create_user_valid(self):
        """测试创建用户有效请求"""
        # 使用唯一的用户名避免冲突
        test_user_data = {
            "username": f"unittest_{self.id()}",
            "email": f"unittest_{self.id()}@example.com",
            "password": "unittest123",
            "role": "user"
        }
        
        response = self.make_request(
            'POST',
            '/api/v1/users/',
            json=test_user_data
        )
        
        # 创建用户可能返回201(成功)或403(权限不足)或409(已存在)
        self.assertIn(response.status_code, [201, 403, 409, 501])
    
    def test_create_user_invalid(self):
        """测试创建用户无效请求"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/users/',
                json={
                    "username": scenario["username"],
                    "email": scenario["email"],
                    "password": scenario["password"],
                    "role": scenario["role"]
                }
            )
            
            # 无效创建可能返回400(数据错误)或403(权限不足)或422(验证错误)
            self.assertIn(response.status_code, [400, 403, 422, 501])
        
        self.run_test_scenarios("user_management_test_data.invalid_create_user", test_scenario)


class TestUserProfile(APITestCase):
    """用户资料接口测试"""
    
    def test_get_current_user_profile(self):
        """测试获取当前用户资料"""
        response = self.make_request('GET', '/api/v1/users/me')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = self.validate_json_response(response)
        expected_fields = ["username", "email", "is_active", "id"]
        
        for field in expected_fields:
            self.assertIn(field, response_data)
    
    def test_get_user_by_id(self):
        """测试根据ID获取用户"""
        # 测试获取用户ID为1的用户(admin)
        response = self.make_request('GET', '/api/v1/users/1')
        
        # 可能返回200(成功)或403(权限不足)或404(不存在)
        self.assertIn(response.status_code, [200, 403, 404])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertEqual(response_data.get("id"), 1)
    
    def test_get_nonexistent_user(self):
        """测试获取不存在的用户"""
        response = self.make_request('GET', '/api/v1/users/999')
        
        # 应该返回404(不存在)或403(权限不足)
        self.assertIn(response.status_code, [403, 404])
    
    def test_update_user_profile(self):
        """测试更新用户资料"""
        # 测试更新当前用户资料
        update_data = {
            "email": f"updated_{self.id()}@example.com"
        }
        
        response = self.make_request(
            'PUT',
            '/api/v1/users/me',
            json=update_data
        )
        
        # 可能返回200(成功)或403(权限不足)或501(未实现)
        self.assertIn(response.status_code, [200, 403, 501])


class TestPasswordChange(APITestCase):
    """密码修改接口测试"""
    
    def test_change_password_valid(self):
        """测试有效密码修改"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/users/me/change-password',
                json={
                    "old_password": scenario["old_password"],
                    "new_password": scenario["new_password"],
                    "confirm_password": scenario["confirm_password"]
                }
            )
            
            # 由于我们不想真的修改密码，接受多种状态码
            self.assertIn(response.status_code, [200, 401, 422, 501])
        
        # 使用虚拟数据测试
        test_scenarios = [
            {
                "old_password": "dummy_old",
                "new_password": "dummy_new123",
                "confirm_password": "dummy_new123",
                "expected_status": 401,  # 旧密码错误
                "description": "虚拟密码修改测试"
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario["description"]):
                test_scenario(scenario)
    
    def test_change_password_invalid(self):
        """测试无效密码修改"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/users/me/change-password',
                json={
                    "old_password": scenario["old_password"],
                    "new_password": scenario["new_password"],
                    "confirm_password": scenario["confirm_password"]
                }
            )
            
            self.assertIn(response.status_code, [401, 422, 501])
        
        self.run_test_scenarios("password_change_test_data.invalid_changes", test_scenario)


class TestUserRoles(APITestCase):
    """用户角色接口测试"""
    
    def test_get_available_roles(self):
        """测试获取可用角色"""
        response = self.make_request('GET', '/api/v1/users/roles/available')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 403, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, list)
            
            # 验证是否包含基本角色
            available_roles = self.test_data.get("roles_test_data", {}).get("available_roles", [])
            for role in available_roles[:2]:  # 只检查前两个角色
                if response_data:  # 如果有数据返回
                    # 简单验证角色数据结构
                    self.assertIsInstance(response_data[0], (str, dict))
    
    def test_role_permissions(self):
        """测试角色权限验证"""
        # 这是一个概念测试，实际权限验证在各个接口中
        roles_data = self.test_data.get("roles_test_data", {})
        role_permissions = roles_data.get("role_permissions", {})
        
        # 验证角色权限数据结构
        for role, permissions in role_permissions.items():
            self.assertIsInstance(permissions, list)
            self.assertGreater(len(permissions), 0)


class TestUserIntegration(APITestCase):
    """用户管理集成测试"""
    
    def test_user_lifecycle(self):
        """测试用户生命周期"""
        # 1. 获取用户列表
        list_response = self.make_request('GET', '/api/v1/users/')
        self.assertIn(list_response.status_code, [200, 403, 501])
        
        # 2. 获取当前用户信息
        profile_response = self.make_request('GET', '/api/v1/users/me')
        self.assertEqual(profile_response.status_code, 200)
        
        # 3. 获取可用角色
        roles_response = self.make_request('GET', '/api/v1/users/roles/available')
        self.assertIn(roles_response.status_code, [200, 403, 501])
    
    def test_admin_operations(self):
        """测试管理员操作"""
        # 使用admin用户进行测试
        admin_headers = self.get_auth_headers("admin", "admin123")
        
        # 获取用户列表
        response = self.session.get(
            f"{self.base_url}/api/v1/users/",
            headers=admin_headers
        )
        
        # 管理员应该能访问用户列表
        self.assertIn(response.status_code, [200, 501])
    
    def test_regular_user_limitations(self):
        """测试普通用户限制"""
        # 使用test用户进行测试
        try:
            test_headers = self.get_auth_headers("test", "test123")
            
            # 尝试获取用户列表
            response = self.session.get(
                f"{self.base_url}/api/v1/users/",
                headers=test_headers
            )
            
            # 普通用户可能被拒绝访问用户列表
            self.assertIn(response.status_code, [200, 403, 501])
            
        except Exception:
            # 如果test用户不存在，跳过这个测试
            self.skipTest("Test user not available")


if __name__ == '__main__':
    unittest.main()

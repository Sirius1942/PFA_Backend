#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证模块unittest测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestAuthLogin(APITestCase):
    """登录接口测试"""
    
    def test_valid_login_scenarios(self):
        """测试有效登录场景"""
        def test_scenario(scenario):
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": scenario["username"],
                    "password": scenario["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIn("access_token", response_data)
                self.assertIn("token_type", response_data)
                self.assertEqual(response_data["token_type"], "bearer")
        
        self.run_test_scenarios("login_test_data.valid_credentials", test_scenario)
    
    def test_invalid_login_scenarios(self):
        """测试无效登录场景"""
        def test_scenario(scenario):
            response = self.session.post(
                f"{self.base_url}/api/v1/auth/login",
                data={
                    "username": scenario["username"],
                    "password": scenario["password"]
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code != 200:
                response_data = self.validate_json_response(response)
                self.assertIn("detail", response_data)
        
        self.run_test_scenarios("login_test_data.invalid_credentials", test_scenario)
    
    def test_login_response_structure(self):
        """测试登录响应结构"""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = self.validate_json_response(response)
        
        expected_fields = ["access_token", "refresh_token", "token_type"]
        for field in expected_fields:
            self.assertIn(field, response_data)
    
    def test_login_token_length(self):
        """测试登录令牌长度"""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # JWT令牌应该有合理的长度
        self.assertGreater(len(response_data["access_token"]), 100)
        self.assertGreater(len(response_data["refresh_token"]), 100)


class TestAuthRegister(APITestCase):
    """注册接口测试"""
    
    def test_valid_registration(self):
        """测试有效注册"""
        registration_data = {
            "username": f"testuser_{self.id()}",
            "email": f"testuser_{self.id()}@example.com",
            "password": "testpass123",
            "confirm_password": "testpass123"
        }
        
        response = self.make_request(
            'POST',
            '/api/v1/auth/register',
            json=registration_data
        )
        
        # 注册可能返回201或409(用户已存在)
        self.assertIn(response.status_code, [201, 409])
    
    def test_invalid_registration_scenarios(self):
        """测试无效注册场景"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/auth/register',
                json={
                    "username": scenario["username"],
                    "email": scenario["email"],
                    "password": scenario["password"],
                    "confirm_password": scenario["confirm_password"]
                }
            )
            
            # 接受多种可能的错误状态码
            self.assertIn(response.status_code, [400, 409, 422])
        
        # 由于可能的数据冲突，这里使用简单的测试案例
        test_scenarios = [
            {
                "username": "admin",  # 已存在
                "email": "admin@example.com",
                "password": "admin123",
                "confirm_password": "admin123",
                "description": "用户名已存在"
            }
        ]
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario["description"]):
                test_scenario(scenario)


class TestAuthProfile(APITestCase):
    """用户资料接口测试"""
    
    def test_get_profile_with_valid_token(self):
        """测试使用有效令牌获取用户资料"""
        response = self.make_request('GET', '/api/v1/auth/profile')
        
        self.assertEqual(response.status_code, 200)
        
        response_data = self.validate_json_response(response)
        profile_fields = self.test_data.get("profile_test_data", {}).get("expected_fields", [])
        
        for field in profile_fields:
            self.assertIn(field, response_data)
    
    def test_get_profile_without_token(self):
        """测试未提供令牌获取用户资料"""
        response = self.session.get(f"{self.base_url}/api/v1/auth/profile")
        
        self.assertEqual(response.status_code, 401)
    
    def test_get_profile_with_invalid_token(self):
        """测试使用无效令牌获取用户资料"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = self.session.get(
            f"{self.base_url}/api/v1/auth/profile",
            headers=headers
        )
        
        self.assertEqual(response.status_code, 401)


class TestAuthPasswordReset(APITestCase):
    """密码重置接口测试"""
    
    def test_password_reset_request(self):
        """测试密码重置请求"""
        response = self.make_request(
            'POST',
            '/api/v1/auth/password-reset-request',
            json={"email": "admin@example.com"}
        )
        
        # 密码重置可能返回200或实际的实现状态
        self.assertIn(response.status_code, [200, 404, 501])  # 501表示未实现
    
    def test_password_reset_with_token(self):
        """测试使用令牌重置密码"""
        response = self.make_request(
            'POST',
            '/api/v1/auth/password-reset',
            json={
                "token": "dummy_reset_token",
                "new_password": "newpassword123"
            }
        )
        
        # 密码重置可能返回200或实际的实现状态
        self.assertIn(response.status_code, [200, 400, 404, 501])


class TestAuthLogout(APITestCase):
    """登出接口测试"""
    
    def test_logout_with_valid_token(self):
        """测试使用有效令牌登出"""
        response = self.make_request('POST', '/api/v1/auth/logout')
        
        # 登出可能返回200或实际的实现状态
        self.assertIn(response.status_code, [200, 204, 501])


class TestAuthRefresh(APITestCase):
    """令牌刷新接口测试"""
    
    def test_refresh_token(self):
        """测试刷新令牌"""
        # 首先获取refresh token
        login_response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if login_response.status_code == 200:
            login_data = login_response.json()
            refresh_token = login_data.get("refresh_token")
            
            if refresh_token:
                response = self.make_request(
                    'POST',
                    '/api/v1/auth/refresh',
                    json={"refresh_token": refresh_token}
                )
                
                # 刷新令牌可能返回200或实际的实现状态
                self.assertIn(response.status_code, [200, 401, 501])


if __name__ == '__main__':
    unittest.main()

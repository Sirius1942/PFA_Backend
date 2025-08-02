#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试基类
提供通用的测试方法和工具
"""

import unittest
import yaml
import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List


class BaseTestCase(unittest.TestCase):
    """测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        cls.base_url = "http://localhost:8000"
        cls.test_data = cls.load_test_data()
        cls.auth_token = None
        cls.session = requests.Session()
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        if cls.session:
            cls.session.close()
    
    def setUp(self):
        """每个测试方法前执行"""
        pass
    
    def tearDown(self):
        """每个测试方法后执行"""
        pass
    
    @classmethod
    def load_test_data(cls) -> Dict[str, Any]:
        """加载测试数据"""
        # 获取当前测试类所在的模块路径
        test_file = Path(cls.__module__.replace('.', '/') + '.py')
        data_dir = test_file.parent.parent / 'data'
        data_file = data_dir / 'test_data.yaml'
        
        if data_file.exists():
            with open(data_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        else:
            return {}
    
    def get_auth_token(self, username: str = "admin", password: str = "admin123") -> str:
        """获取认证令牌"""
        if self.auth_token:
            return self.auth_token
        
        login_data = {
            "username": username,
            "password": password
        }
        
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            token_data = response.json()
            self.auth_token = token_data["access_token"]
            return self.auth_token
        else:
            self.fail(f"Failed to get auth token: {response.status_code} - {response.text}")
    
    def get_auth_headers(self, username: str = "admin", password: str = "admin123") -> Dict[str, str]:
        """获取认证头"""
        token = self.get_auth_token(username, password)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        
        # 如果需要认证且未提供headers，自动添加认证头
        if 'headers' not in kwargs and endpoint.startswith('/api/v1') and endpoint not in ['/api/v1/auth/login', '/api/v1/auth/register']:
            kwargs['headers'] = self.get_auth_headers()
        
        return self.session.request(method, url, **kwargs)
    
    def assert_response_structure(self, response: requests.Response, expected_fields: List[str]):
        """断言响应结构"""
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        for field in expected_fields:
            self.assertIn(field, response_data, f"Expected field '{field}' not found in response")
    
    def assert_error_response(self, response: requests.Response, expected_status: int, expected_detail: str = None):
        """断言错误响应"""
        self.assertEqual(response.status_code, expected_status)
        
        if expected_detail:
            response_data = response.json()
            self.assertIn("detail", response_data)
            self.assertIn(expected_detail, response_data["detail"])
    
    def run_test_scenarios(self, test_data_key: str, test_method):
        """运行测试场景"""
        test_scenarios = self.test_data.get(test_data_key, [])
        
        for scenario in test_scenarios:
            with self.subTest(scenario=scenario.get('description', 'Unknown scenario')):
                test_method(scenario)
    
    def validate_json_response(self, response: requests.Response) -> Dict[str, Any]:
        """验证JSON响应"""
        self.assertEqual(response.headers.get('content-type', '').split(';')[0], 'application/json')
        
        try:
            return response.json()
        except json.JSONDecodeError:
            self.fail(f"Invalid JSON response: {response.text}")


class APITestCase(BaseTestCase):
    """API测试基类"""
    
    def test_endpoint_accessibility(self):
        """测试端点可访问性"""
        response = self.make_request('GET', '/health')
        self.assertEqual(response.status_code, 200)
    
    def test_api_documentation(self):
        """测试API文档可访问性"""
        endpoints = ['/docs', '/redoc', '/openapi.json']
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = requests.get(f"{self.base_url}{endpoint}")
                self.assertEqual(response.status_code, 200)


class DatabaseTestCase(BaseTestCase):
    """数据库测试基类"""
    
    def setUp(self):
        """数据库测试初始化"""
        super().setUp()
        # 这里可以添加数据库连接和测试数据准备
        pass
    
    def tearDown(self):
        """数据库测试清理"""
        super().tearDown()
        # 这里可以添加测试数据清理
        pass

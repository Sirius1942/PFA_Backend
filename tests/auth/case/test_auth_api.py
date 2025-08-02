#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证API测试用例
从yaml数据文件读取测试数据
"""

import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any


class TestAuthAPI:
    """认证API测试类"""
    
    @classmethod
    def setup_class(cls):
        """加载测试数据"""
        data_file = Path(__file__).parent.parent / "data" / "test_data.yaml"
        with open(data_file, 'r', encoding='utf-8') as f:
            cls.test_data = yaml.safe_load(f)
        cls.base_url = cls.test_data['api_endpoints']['base_url']
    
    def test_load_yaml_data(self):
        """测试yaml数据加载"""
        assert self.test_data is not None
        assert 'users' in self.test_data
        assert 'login_scenarios' in self.test_data
        assert 'api_endpoints' in self.test_data
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['login_scenarios']
    ])
    def test_login_scenarios(self, scenario):
        """测试各种登录场景"""
        login_url = f"{self.base_url}{self.test_data['api_endpoints']['login']}"
        
        # 准备请求数据
        data = {}
        if 'username' in scenario:
            data['username'] = scenario['username']
        if 'password' in scenario:
            data['password'] = scenario['password']
        
        # 发送请求
        response = requests.post(
            login_url,
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功场景的响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            for field in scenario.get('expected_fields', []):
                assert field in response_data, f"响应中缺少字段: {field}"
            
            # 验证token类型
            if 'token_type' in response_data:
                assert response_data['token_type'] == 'bearer'
        
        # 验证错误场景的响应
        elif 'expected_error' in scenario:
            response_data = response.json()
            assert 'detail' in response_data
            assert scenario['expected_error'] in response_data['detail']
    
    def test_admin_login_success(self):
        """测试管理员登录成功"""
        admin_user = self.test_data['users']['admin']
        login_url = f"{self.base_url}{self.test_data['api_endpoints']['login']}"
        
        response = requests.post(
            login_url,
            data={
                'username': admin_user['username'],
                'password': admin_user['password']
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        assert response.status_code == admin_user['expected_status']
        response_data = response.json()
        assert 'access_token' in response_data
        assert 'refresh_token' in response_data
        assert response_data['token_type'] == 'bearer'
        
        # 保存token用于后续测试
        self.admin_token = response_data['access_token']
    
    def test_protected_endpoints(self):
        """测试受保护的端点"""
        # 先获取token
        admin_user = self.test_data['users']['admin']
        login_url = f"{self.base_url}{self.test_data['api_endpoints']['login']}"
        
        login_response = requests.post(
            login_url,
            data={
                'username': admin_user['username'],
                'password': admin_user['password']
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        
        token = login_response.json()['access_token']
        
        # 测试受保护的端点
        for endpoint_data in self.test_data['protected_endpoints']:
            endpoint_url = f"{self.base_url}{endpoint_data['endpoint']}"
            headers = {"Authorization": f"Bearer {token}"}
            
            if endpoint_data['method'] == 'GET':
                response = requests.get(endpoint_url, headers=headers, timeout=10)
            elif endpoint_data['method'] == 'POST':
                response = requests.post(endpoint_url, headers=headers, timeout=10)
            
            assert response.status_code == endpoint_data['expected_status']
            
            if endpoint_data['expected_status'] == 200:
                response_data = response.json()
                for field in endpoint_data.get('expected_fields', []):
                    assert field in response_data, f"响应中缺少字段: {field}"
    
    def test_unauthorized_access(self):
        """测试未授权访问"""
        profile_url = f"{self.base_url}{self.test_data['api_endpoints']['profile']}"
        
        # 不带token的请求
        response = requests.get(profile_url, timeout=10)
        assert response.status_code == 401
        
        # 带无效token的请求
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(profile_url, headers=headers, timeout=10)
        assert response.status_code == 401
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['register_scenarios']
    ])
    def test_register_scenarios(self, scenario):
        """测试用户注册场景"""
        register_url = f"{self.base_url}{self.test_data['api_endpoints']['register']}"
        
        # 准备请求数据
        data = {}
        for key in ['username', 'email', 'password', 'confirm_password']:
            if key in scenario:
                data[key] = scenario[key]
        
        # 发送请求
        response = requests.post(
            register_url,
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"注册场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证错误场景的响应
        if 'expected_error' in scenario and scenario['expected_status'] != 201:
            response_data = response.json()
            assert 'detail' in response_data or 'message' in response_data

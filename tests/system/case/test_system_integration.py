#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成测试用例
从yaml数据文件读取测试数据
"""

import pytest
import yaml
import requests
import pymysql
import time
from pathlib import Path
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class TestSystemIntegration:
    """系统集成测试类"""
    
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
        assert 'database_config' in self.test_data
        assert 'health_check_scenarios' in self.test_data
        assert 'api_endpoints' in self.test_data
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['health_check_scenarios']
    ])
    def test_health_check_scenarios(self, scenario):
        """测试健康检查场景"""
        endpoint_url = f"{self.base_url}{scenario['endpoint']}"
        
        response = requests.get(endpoint_url, timeout=10)
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"健康检查场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证内容类型
        if 'expected_content_type' in scenario:
            content_type = response.headers.get('content-type', '')
            assert scenario['expected_content_type'] in content_type, \
                f"内容类型不匹配: 期望 {scenario['expected_content_type']}, 实际 {content_type}"
        
        # 验证响应字段
        if scenario['expected_status'] == 200 and 'expected_fields' in scenario:
            response_data = response.json()
            for field in scenario['expected_fields']:
                assert field in response_data, f"响应中缺少字段: {field}"
            
            # 验证特定值
            if 'expected_values' in scenario:
                for field, expected_value in scenario['expected_values'].items():
                    assert response_data[field] == expected_value, \
                        f"字段 {field} 值不匹配: 期望 {expected_value}, 实际 {response_data[field]}"
    
    def test_database_connection(self):
        """测试数据库连接"""
        db_config = self.test_data['database_config']['mysql']
        
        try:
            connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password']
            )
            
            cursor = connection.cursor()
            
            # 执行连接测试
            connection_test = self.test_data['database_tests']['connection_test']
            cursor.execute(connection_test['query'])
            result = cursor.fetchone()
            
            assert result == tuple(connection_test['expected_result']), \
                f"数据库连接测试失败: 期望 {connection_test['expected_result']}, 实际 {result}"
            
            # 测试用户数量
            user_count_test = self.test_data['database_tests']['user_count_test']
            cursor.execute(user_count_test['query'])
            count = cursor.fetchone()[0]
            
            assert count >= user_count_test['expected_min_count'], \
                f"用户数量不足: 期望至少 {user_count_test['expected_min_count']}, 实际 {count}"
            
            connection.close()
            
        except Exception as e:
            pytest.fail(f"数据库连接失败: {e}")
    
    def test_database_tables_exist(self):
        """测试数据库表是否存在"""
        db_config = self.test_data['database_config']['mysql']
        
        try:
            connection = pymysql.connect(
                host=db_config['host'],
                port=db_config['port'],
                database=db_config['database'],
                user=db_config['user'],
                password=db_config['password']
            )
            
            cursor = connection.cursor()
            
            # 获取所有表名
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            # 验证期望的表都存在
            expected_tables = self.test_data['database_tests']['tables_exist_test']['expected_tables']
            for table in expected_tables:
                assert table in existing_tables, f"表 {table} 不存在"
            
            connection.close()
            
        except Exception as e:
            pytest.fail(f"数据库表检查失败: {e}")
    
    @pytest.mark.parametrize("test_config", [
        test_config for test_config in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['performance_tests']['api_response_times'].values()
    ])
    def test_api_performance(self, test_config):
        """测试API性能"""
        endpoint_url = f"{self.base_url}{test_config['endpoint']}"
        
        # 准备请求参数
        params = test_config.get('params', {})
        headers = {}
        
        # 如果需要认证，获取token
        if test_config.get('requires_auth', False):
            token = self._get_auth_token()
            headers['Authorization'] = f'Bearer {token}'
        
        # 测试响应时间
        start_time = time.time()
        response = requests.get(endpoint_url, params=params, headers=headers, timeout=10)
        end_time = time.time()
        
        response_time_ms = (end_time - start_time) * 1000
        
        # 验证响应时间
        max_time = test_config['max_response_time_ms']
        assert response_time_ms <= max_time, \
            f"API响应时间超限: {response_time_ms:.2f}ms > {max_time}ms"
        
        # 验证响应状态
        assert response.status_code in [200, 401], "API应返回成功或未授权状态"
    
    def test_full_user_flow_integration(self):
        """测试完整用户流程集成"""
        flow = self.test_data['integration_tests']['full_user_flow']
        token = None
        
        for step in flow['steps']:
            endpoint_url = f"{self.base_url}{step['endpoint']}"
            
            # 准备请求头
            headers = {"Content-Type": "application/json"}
            if step.get('requires_auth', False) and token:
                headers['Authorization'] = f'Bearer {token}'
            
            # 准备请求数据
            data = step.get('data', {})
            params = step.get('params', {})
            
            # 发送请求
            if step['method'] == 'POST':
                if step['endpoint'] == '/api/v1/auth/login':
                    # 登录接口使用form数据
                    headers['Content-Type'] = 'application/x-www-form-urlencoded'
                    response = requests.post(endpoint_url, data=data, headers=headers, timeout=10)
                else:
                    response = requests.post(endpoint_url, json=data, headers=headers, timeout=30)
            elif step['method'] == 'GET':
                response = requests.get(endpoint_url, params=params, headers=headers, timeout=10)
            
            # 验证响应状态码
            assert response.status_code == step['expected_status'], \
                f"步骤 {step['name']} 失败: 期望状态码 {step['expected_status']}, 实际 {response.status_code}"
            
            # 提取token用于后续步骤
            if step.get('extract_token', False) and response.status_code == 200:
                response_data = response.json()
                token = response_data.get('access_token')
                assert token, "未能获取访问令牌"
    
    @pytest.mark.parametrize("error_scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['error_scenarios']['server_errors']
    ])
    def test_server_error_scenarios(self, error_scenario):
        """测试服务器错误场景"""
        endpoint_url = f"{self.base_url}{error_scenario['endpoint']}"
        
        method = error_scenario.get('method', 'GET')
        
        if method == 'GET':
            response = requests.get(endpoint_url, timeout=10)
        elif method == 'POST':
            response = requests.post(endpoint_url, timeout=10)
        
        assert response.status_code == error_scenario['expected_status'], \
            f"错误场景 {error_scenario['name']} 失败: 期望状态码 {error_scenario['expected_status']}, 实际 {response.status_code}"
    
    @pytest.mark.parametrize("error_scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['error_scenarios']['client_errors']
    ])
    def test_client_error_scenarios(self, error_scenario):
        """测试客户端错误场景"""
        endpoint_url = f"{self.base_url}{error_scenario['endpoint']}"
        
        method = error_scenario.get('method', 'GET')
        headers = error_scenario.get('headers', {"Content-Type": "application/json"})
        
        if method == 'POST':
            if 'raw_data' in error_scenario:
                # 发送原始数据（可能是格式错误的JSON）
                response = requests.post(
                    endpoint_url, 
                    data=error_scenario['raw_data'], 
                    headers=headers, 
                    timeout=10
                )
            else:
                # 发送JSON数据
                data = error_scenario.get('data', {})
                response = requests.post(endpoint_url, json=data, headers=headers, timeout=10)
        
        assert response.status_code == error_scenario['expected_status'], \
            f"客户端错误场景 {error_scenario['name']} 失败: 期望状态码 {error_scenario['expected_status']}, 实际 {response.status_code}"
    
    def test_frontend_integration(self):
        """测试前端集成"""
        frontend_config = self.test_data.get('frontend_integration', {})
        
        if not frontend_config:
            pytest.skip("未配置前端集成测试")
        
        frontend_url = frontend_config['frontend_url']
        
        for endpoint in frontend_config['endpoints']:
            endpoint_url = f"{frontend_url}{endpoint['path']}"
            
            try:
                response = requests.get(endpoint_url, timeout=5)
                assert response.status_code == endpoint['expected_status'], \
                    f"前端页面 {endpoint['path']} 返回状态码 {response.status_code}"
                
                # 如果期望特定标题
                if 'expected_title' in endpoint:
                    assert endpoint['expected_title'] in response.text
                    
            except requests.exceptions.ConnectionError:
                pytest.skip(f"前端服务 {frontend_url} 不可用")
    
    def _get_auth_token(self) -> str:
        """获取认证token的辅助方法"""
        login_url = f"{self.base_url}/api/v1/auth/login"
        response = requests.post(
            login_url,
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['access_token']
        return ""
    
    @pytest.mark.slow
    def test_load_test(self):
        """简单的负载测试"""
        load_config = self.test_data.get('load_tests', {})
        
        if not load_config:
            pytest.skip("未配置负载测试")
        
        concurrent_users = load_config['concurrent_users']
        test_duration = load_config['test_duration_seconds']
        endpoints = load_config['endpoints']
        
        # 获取认证token
        auth_token = self._get_auth_token()
        
        def make_request(endpoint_config):
            """发送单个请求"""
            endpoint_url = f"{self.base_url}{endpoint_config['endpoint']}"
            headers = {}
            
            if endpoint_config.get('requires_auth', False):
                headers['Authorization'] = f'Bearer {auth_token}'
            
            if 'data' in endpoint_config:
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
                response = requests.post(endpoint_url, data=endpoint_config['data'], headers=headers, timeout=10)
            else:
                params = endpoint_config.get('params', {})
                response = requests.get(endpoint_url, params=params, headers=headers, timeout=10)
            
            return response.status_code
        
        # 并发测试
        start_time = time.time()
        successful_requests = 0
        total_requests = 0
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            while time.time() - start_time < test_duration:
                # 选择一个端点（可以基于权重）
                endpoint = endpoints[0]  # 简化版本，选择第一个
                
                future = executor.submit(make_request, endpoint)
                total_requests += 1
                
                try:
                    status_code = future.result(timeout=10)
                    if status_code in [200, 401]:  # 认为200和401都是成功的响应
                        successful_requests += 1
                except Exception:
                    pass  # 请求失败
        
        # 验证成功率
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        assert success_rate >= 0.8, f"成功率过低: {success_rate:.2%} < 80%"

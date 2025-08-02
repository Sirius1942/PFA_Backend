#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手API测试用例
从yaml数据文件读取测试数据
"""

import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any


class TestAssistantAPI:
    """AI助手API测试类"""
    
    @classmethod
    def setup_class(cls):
        """加载测试数据和获取认证token"""
        data_file = Path(__file__).parent.parent / "data" / "test_data.yaml"
        with open(data_file, 'r', encoding='utf-8') as f:
            cls.test_data = yaml.safe_load(f)
        cls.base_url = cls.test_data['api_endpoints']['base_url']
        
        # 获取认证token
        cls.auth_token = cls._get_auth_token()
    
    @classmethod
    def _get_auth_token(cls) -> str:
        """获取认证token"""
        login_url = f"{cls.base_url}/api/v1/auth/login"
        response = requests.post(
            login_url,
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10
        )
        if response.status_code == 200:
            return response.json()['access_token']
        return ""
    
    def get_auth_headers(self) -> Dict[str, str]:
        """获取认证请求头"""
        return {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['chat_scenarios']
    ])
    def test_chat_scenarios(self, scenario):
        """测试AI聊天场景"""
        chat_url = f"{self.base_url}{self.test_data['api_endpoints']['chat']}"
        
        # 准备请求数据
        data = {}
        if 'message' in scenario:
            data['message'] = scenario['message']
        
        # 发送请求
        response = requests.post(
            chat_url,
            json=data,
            headers=self.get_auth_headers(),
            timeout=30  # AI响应可能较慢
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"聊天场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            assert 'response' in response_data or 'message' in response_data, "响应中应包含回复内容"
            
            # 验证关键词
            response_text = response_data.get('response', response_data.get('message', ''))
            for keyword in scenario.get('expected_keywords', []):
                assert keyword in response_text, f"响应中应包含关键词: {keyword}"
        
        # 验证错误响应
        elif 'expected_error' in scenario:
            response_data = response.json()
            assert 'detail' in response_data or 'error' in response_data
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['stock_analysis_scenarios']
    ])
    def test_stock_analysis_scenarios(self, scenario):
        """测试股票分析场景"""
        analyze_url = f"{self.base_url}{self.test_data['api_endpoints']['analyze_stock']}"
        
        # 准备请求数据
        data = {
            'stock_code': scenario['stock_code'],
            'analysis_type': scenario['analysis_type']
        }
        
        # 设置请求头
        headers = self.get_auth_headers() if scenario.get('requires_auth', True) else {}
        if headers:
            headers['Content-Type'] = 'application/json'
        
        # 发送请求
        response = requests.post(
            analyze_url,
            json=data,
            headers=headers,
            timeout=30
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"分析场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            for field in scenario.get('expected_fields', []):
                assert field in response_data, f"分析响应中缺少字段: {field}"
            
            # 验证股票代码
            if 'code' in response_data:
                assert response_data['code'] == scenario['stock_code']
        
        # 验证错误响应
        elif 'expected_error' in scenario:
            response_data = response.json()
            assert 'detail' in response_data or 'error' in response_data
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['market_insights_scenarios']
    ])
    def test_market_insights_scenarios(self, scenario):
        """测试市场洞察场景"""
        insights_url = f"{self.base_url}{self.test_data['api_endpoints']['market_insights']}"
        
        # 准备请求参数
        params = {}
        if 'timeframe' in scenario:
            params['timeframe'] = scenario['timeframe']
        
        # 发送请求
        response = requests.get(
            insights_url,
            params=params,
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"洞察场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            for field in scenario.get('expected_fields', []):
                assert field in response_data, f"洞察响应中缺少字段: {field}"
        
        # 验证错误响应
        elif 'expected_error' in scenario:
            response_data = response.json()
            assert 'detail' in response_data or 'error' in response_data
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['conversation_history_scenarios']
    ])
    def test_conversation_history_scenarios(self, scenario):
        """测试对话历史场景"""
        history_url = f"{self.base_url}{self.test_data['api_endpoints']['conversation_history']}"
        
        # 准备请求参数
        params = {}
        if 'user_id' in scenario:
            params['user_id'] = scenario['user_id']
        if 'limit' in scenario:
            params['limit'] = scenario['limit']
        
        # 发送请求
        response = requests.get(
            history_url,
            params=params,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"历史场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            for field in scenario.get('expected_fields', []):
                assert field in response_data, f"历史响应中缺少字段: {field}"
            
            # 验证结果数量
            if 'expected_results' in scenario:
                conversations = response_data.get('conversations', [])
                assert len(conversations) == scenario['expected_results']
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['suggestions_scenarios']
    ])
    def test_suggestions_scenarios(self, scenario):
        """测试建议场景"""
        suggestions_url = f"{self.base_url}{self.test_data['api_endpoints']['suggestions']}"
        
        # 准备请求参数
        params = {}
        if 'context' in scenario:
            params['context'] = scenario['context']
        if 'stock_code' in scenario:
            params['stock_code'] = scenario['stock_code']
        
        # 发送请求
        response = requests.get(
            suggestions_url,
            params=params,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"建议场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            for field in scenario.get('expected_fields', []):
                assert field in response_data, f"建议响应中缺少字段: {field}"
            
            # 验证建议数量
            if 'expected_min_suggestions' in scenario:
                suggestions = response_data.get('suggestions', [])
                assert len(suggestions) >= scenario['expected_min_suggestions']
    
    def test_ai_chat_basic(self):
        """测试基本AI聊天功能"""
        chat_url = f"{self.base_url}{self.test_data['api_endpoints']['chat']}"
        
        response = requests.post(
            chat_url,
            json={"message": "你好"},
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert 'response' in response_data or 'message' in response_data
    
    def test_stock_analysis_basic(self):
        """测试基本股票分析功能"""
        analyze_url = f"{self.base_url}{self.test_data['api_endpoints']['analyze_stock']}"
        
        response = requests.post(
            analyze_url,
            json={
                "stock_code": "000001",
                "analysis_type": "technical"
            },
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        # 可能返回200（成功）或502（AI服务不可用）
        assert response.status_code in [200, 502, 503]
        
        if response.status_code == 200:
            response_data = response.json()
            assert 'analysis' in response_data or 'code' in response_data
    
    def test_unauthorized_access(self):
        """测试未授权访问AI助手接口"""
        chat_url = f"{self.base_url}{self.test_data['api_endpoints']['chat']}"
        
        # 不带token的请求
        response = requests.post(
            chat_url,
            json={"message": "测试"},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        assert response.status_code == 401
        
        # 带无效token的请求
        headers = {
            "Authorization": "Bearer invalid_token",
            "Content-Type": "application/json"
        }
        response = requests.post(
            chat_url,
            json={"message": "测试"},
            headers=headers,
            timeout=10
        )
        assert response.status_code == 401

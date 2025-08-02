#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票API测试用例
从yaml数据文件读取测试数据
"""

import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, Any, List


class TestStocksAPI:
    """股票API测试类"""
    
    @classmethod
    def setup_class(cls):
        """加载测试数据和获取认证token"""
        data_file = Path(__file__).parent.parent / "data" / "test_data.yaml"
        with open(data_file, 'r', encoding='utf-8') as f:
            cls.test_data = yaml.safe_load(f)
        cls.base_url = cls.test_data['api_endpoints']['base_url']
        
        # 获取认证token用于需要认证的接口
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
        return {"Authorization": f"Bearer {self.auth_token}"}
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['search_scenarios']
    ])
    def test_stock_search_scenarios(self, scenario):
        """测试股票搜索场景"""
        search_url = f"{self.base_url}{self.test_data['api_endpoints']['search']}"
        
        # 准备请求参数
        params = {}
        if scenario.get('query') is not None:
            params['q'] = scenario['query']
        
        # 发送请求
        response = requests.get(
            search_url,
            params=params,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"搜索场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应
        if scenario['expected_status'] == 200:
            response_data = response.json()
            
            # 验证最小结果数量
            if 'expected_min_results' in scenario:
                assert len(response_data) >= scenario['expected_min_results'], \
                    f"结果数量不足: 期望至少 {scenario['expected_min_results']}, 实际 {len(response_data)}"
            
            # 验证精确结果数量
            if 'expected_results' in scenario:
                assert len(response_data) == scenario['expected_results'], \
                    f"结果数量不匹配: 期望 {scenario['expected_results']}, 实际 {len(response_data)}"
    
    @pytest.mark.parametrize("stock", [
        stock for stock in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['test_stocks']['valid_stocks']
    ])
    def test_valid_stock_info(self, stock):
        """测试有效股票信息获取"""
        info_url = f"{self.base_url}{self.test_data['api_endpoints']['info'].format(stock_code=stock['code'])}"
        
        response = requests.get(
            info_url,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        assert response.status_code == 200
        response_data = response.json()
        
        # 验证基本字段
        expected_fields = ["code", "name"]
        for field in expected_fields:
            assert field in response_data, f"响应中缺少字段: {field}"
        
        # 验证股票代码和名称
        assert response_data['code'] == stock['code']
        # 注意: 实际的股票名称可能与测试数据不完全一致，这里只验证不为空
        assert response_data['name'], "股票名称不能为空"
    
    @pytest.mark.parametrize("stock", [
        stock for stock in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['test_stocks']['invalid_stocks']
    ])
    def test_invalid_stock_info(self, stock):
        """测试无效股票信息获取"""
        info_url = f"{self.base_url}{self.test_data['api_endpoints']['info'].format(stock_code=stock['code'])}"
        
        response = requests.get(
            info_url,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        assert response.status_code == stock['expected_status']
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['kline_scenarios']
    ])
    def test_kline_scenarios(self, scenario):
        """测试K线数据获取场景"""
        kline_url = f"{self.base_url}{self.test_data['api_endpoints']['kline'].format(stock_code=scenario['stock_code'])}"
        
        # 准备请求参数
        params = {}
        if 'period' in scenario:
            params['period'] = scenario['period']
        if 'limit' in scenario:
            params['limit'] = scenario['limit']
        
        # 发送请求
        response = requests.get(
            kline_url,
            params=params,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        # 验证状态码
        assert response.status_code == scenario['expected_status'], \
            f"K线场景 {scenario['name']} 失败: 期望状态码 {scenario['expected_status']}, 实际 {response.status_code}"
        
        # 验证成功响应的数据结构
        if scenario['expected_status'] == 200:
            response_data = response.json()
            assert isinstance(response_data, list), "K线数据应该是列表格式"
            
            if response_data:  # 如果有数据
                # 验证数据字段
                for field in scenario.get('expected_fields', []):
                    assert field in response_data[0], f"K线数据中缺少字段: {field}"
    
    @pytest.mark.parametrize("scenario", [
        scenario for scenario in yaml.safe_load(
            open(Path(__file__).parent.parent / "data" / "test_data.yaml", 'r', encoding='utf-8')
        )['realtime_scenarios']
    ])
    def test_realtime_scenarios(self, scenario):
        """测试实时行情场景"""
        if scenario['name'] == 'get_single_realtime':
            # 单个股票实时行情
            realtime_url = f"{self.base_url}{self.test_data['api_endpoints']['realtime_single'].format(stock_code=scenario['stock_code'])}"
            
            response = requests.get(
                realtime_url,
                headers=self.get_auth_headers(),
                timeout=10
            )
            
            assert response.status_code == scenario['expected_status']
            
            if scenario['expected_status'] == 200:
                response_data = response.json()
                for field in scenario.get('expected_fields', []):
                    assert field in response_data, f"实时行情数据中缺少字段: {field}"
        
        elif scenario['name'] == 'get_batch_realtime':
            # 批量股票实时行情
            batch_url = f"{self.base_url}{self.test_data['api_endpoints']['realtime_batch']}"
            
            response = requests.post(
                batch_url,
                json={"codes": scenario['stock_codes']},
                headers={**self.get_auth_headers(), "Content-Type": "application/json"},
                timeout=10
            )
            
            assert response.status_code == scenario['expected_status']
            
            if scenario['expected_status'] == 200:
                response_data = response.json()
                assert len(response_data) >= scenario['expected_min_results']
    
    def test_markets_endpoint(self):
        """测试获取市场列表"""
        markets_url = f"{self.base_url}{self.test_data['api_endpoints']['markets']}"
        
        response = requests.get(
            markets_url,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list), "市场列表应该是数组格式"
    
    def test_industries_endpoint(self):
        """测试获取行业列表"""
        industries_url = f"{self.base_url}{self.test_data['api_endpoints']['industries']}"
        
        response = requests.get(
            industries_url,
            headers=self.get_auth_headers(),
            timeout=10
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list), "行业列表应该是数组格式"
    
    def test_unauthorized_access(self):
        """测试未授权访问股票接口"""
        search_url = f"{self.base_url}{self.test_data['api_endpoints']['search']}"
        
        # 不带token的请求
        response = requests.get(search_url, params={"q": "000001"}, timeout=10)
        assert response.status_code == 401
        
        # 带无效token的请求
        headers = {"Authorization": "Bearer invalid_token"}
        response = requests.get(search_url, params={"q": "000001"}, headers=headers, timeout=10)
        assert response.status_code == 401

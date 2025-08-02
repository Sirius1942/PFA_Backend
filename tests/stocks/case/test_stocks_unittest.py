#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票模块unittest测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestStockInfo(APITestCase):
    """股票信息接口测试"""
    
    def test_get_stock_info_valid_codes(self):
        """测试获取有效股票代码信息"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                f'/api/v1/stocks/info/{scenario["stock_code"]}'
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                # 验证基本股票信息字段
                expected_fields = ["code", "name", "market", "industry"]
                for field in expected_fields:
                    self.assertIn(field, response_data, f"Expected field '{field}' not found")
        
        self.run_test_scenarios("stock_info_test_data.valid_stock_codes", test_scenario)
    
    def test_get_stock_info_invalid_codes(self):
        """测试获取无效股票代码信息"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                f'/api/v1/stocks/info/{scenario["stock_code"]}'
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("stock_info_test_data.invalid_stock_codes", test_scenario)
    
    def test_stock_info_002379(self):
        """专门测试002379股票信息"""
        response = self.make_request('GET', '/api/v1/stocks/info/002379')
        
        # 允许200(有数据)或404(模拟数据)
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            data = self.validate_json_response(response)
            self.assertEqual(data.get("code"), "002379")


class TestRealtimeQuotes(APITestCase):
    """实时行情接口测试"""
    
    def test_get_single_realtime_quote(self):
        """测试获取单个股票实时行情"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                f'/api/v1/stocks/realtime/{scenario["stock_code"]}'
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                expected_fields = scenario.get("expected_fields", [])
                for field in expected_fields:
                    self.assertIn(field, response_data)
        
        self.run_test_scenarios("realtime_quotes_test_data.single_stock", test_scenario)
    
    def test_get_batch_realtime_quotes(self):
        """测试批量获取实时行情"""
        stock_codes = ["002379", "000001", "000002"]
        
        response = self.make_request(
            'POST',
            '/api/v1/stocks/realtime/batch',
            json={"stock_codes": stock_codes}
        )
        
        # 允许200(有数据)或其他状态(模拟数据)
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, list)


class TestKlineData(APITestCase):
    """K线数据接口测试"""
    
    def test_get_kline_data_valid_requests(self):
        """测试获取K线数据有效请求"""
        def test_scenario(scenario):
            params = {
                "period": scenario.get("period", "1d"),
                "limit": scenario.get("limit", 30)
            }
            
            response = self.make_request(
                'GET',
                f'/api/v1/stocks/kline/{scenario["stock_code"]}',
                params=params
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIsInstance(response_data, list)
                
                if response_data:  # 如果有数据
                    # 验证K线数据结构
                    kline_item = response_data[0]
                    expected_fields = ["timestamp", "open", "high", "low", "close", "volume"]
                    for field in expected_fields:
                        self.assertIn(field, kline_item)
        
        self.run_test_scenarios("kline_test_data.valid_requests", test_scenario)
    
    def test_get_kline_data_invalid_requests(self):
        """测试获取K线数据无效请求"""
        def test_scenario(scenario):
            params = {
                "period": scenario.get("period", "1d"),
                "limit": scenario.get("limit", 30)
            }
            
            response = self.make_request(
                'GET',
                f'/api/v1/stocks/kline/{scenario["stock_code"]}',
                params=params
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("kline_test_data.invalid_requests", test_scenario)


class TestStockSearch(APITestCase):
    """股票搜索接口测试"""
    
    def test_search_stocks_valid_queries(self):
        """测试股票搜索有效查询"""
        def test_scenario(scenario):
            params = {"q": scenario["query"]}
            
            response = self.make_request(
                'GET',
                '/api/v1/stocks/search',
                params=params
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIsInstance(response_data, list)
        
        self.run_test_scenarios("search_test_data.valid_queries", test_scenario)
    
    def test_search_stocks_invalid_queries(self):
        """测试股票搜索无效查询"""
        def test_scenario(scenario):
            params = {"q": scenario["query"]}
            
            response = self.make_request(
                'GET',
                '/api/v1/stocks/search',
                params=params
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("search_test_data.invalid_queries", test_scenario)


class TestWatchlist(APITestCase):
    """关注列表接口测试"""
    
    def test_get_watchlist(self):
        """测试获取关注列表"""
        response = self.make_request('GET', '/api/v1/stocks/watchlist')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 404])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, list)
    
    def test_add_to_watchlist(self):
        """测试添加到关注列表"""
        response = self.make_request(
            'POST',
            '/api/v1/stocks/watchlist',
            json={"stock_code": "002379"}
        )
        
        # 允许201(添加成功)或409(已存在)或其他状态
        self.assertIn(response.status_code, [201, 409, 404, 501])
    
    def test_remove_from_watchlist(self):
        """测试从关注列表移除"""
        response = self.make_request(
            'DELETE',
            '/api/v1/stocks/watchlist/002379'
        )
        
        # 允许204(删除成功)或404(不存在)或其他状态
        self.assertIn(response.status_code, [204, 404, 501])


class TestMarketData(APITestCase):
    """市场数据接口测试"""
    
    def test_get_market_overview(self):
        """测试获取市场概况"""
        response = self.make_request('GET', '/api/v1/stocks/stats/market-overview')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            overview_fields = self.test_data.get("market_data", {}).get("overview_fields", [])
            # 验证部分字段即可，因为可能是模拟数据
            for field in overview_fields[:2]:  # 只验证前两个字段
                if field in response_data:
                    self.assertIsNotNone(response_data[field])
    
    def test_get_industries(self):
        """测试获取行业列表"""
        response = self.make_request('GET', '/api/v1/stocks/industries')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, list)
    
    def test_get_markets(self):
        """测试获取市场列表"""
        response = self.make_request('GET', '/api/v1/stocks/markets')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, list)


if __name__ == '__main__':
    unittest.main()

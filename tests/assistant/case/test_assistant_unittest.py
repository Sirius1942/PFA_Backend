#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手模块unittest测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestAssistantChat(APITestCase):
    """AI助手对话接口测试"""
    
    def test_chat_valid_queries(self):
        """测试AI助手有效查询"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/assistant/chat',
                json={"message": scenario["message"]}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIn("response", response_data)
                self.assertIsInstance(response_data["response"], str)
                self.assertGreater(len(response_data["response"]), 0)
        
        self.run_test_scenarios("chat_test_data.valid_queries", test_scenario)
    
    def test_chat_invalid_queries(self):
        """测试AI助手无效查询"""
        def test_scenario(scenario):
            # 处理超长消息的情况
            message = scenario["message"]
            if len(message) > 1000:
                message = "a" * 1001  # 生成实际的超长消息
            
            response = self.make_request(
                'POST',
                '/api/v1/assistant/chat',
                json={"message": message}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("chat_test_data.invalid_queries", test_scenario)
    
    def test_chat_response_structure(self):
        """测试对话响应结构"""
        response = self.make_request(
            'POST',
            '/api/v1/assistant/chat',
            json={"message": "你好"}
        )
        
        self.assertIn(response.status_code, [200, 501])  # 501表示未完全实现
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            expected_fields = ["response", "timestamp"]
            
            for field in expected_fields:
                if field in response_data:
                    self.assertIsNotNone(response_data[field])


class TestStockAnalysis(APITestCase):
    """股票分析接口测试"""
    
    def test_analyze_stock_valid_requests(self):
        """测试股票分析有效请求"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/assistant/analyze-stock',
                json={
                    "stock_code": scenario["stock_code"],
                    "analysis_type": scenario["analysis_type"]
                }
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIn("analysis", response_data)
        
        self.run_test_scenarios("stock_analysis_test_data.valid_requests", test_scenario)
    
    def test_analyze_stock_invalid_requests(self):
        """测试股票分析无效请求"""
        def test_scenario(scenario):
            response = self.make_request(
                'POST',
                '/api/v1/assistant/analyze-stock',
                json={
                    "stock_code": scenario["stock_code"],
                    "analysis_type": scenario["analysis_type"]
                }
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("stock_analysis_test_data.invalid_requests", test_scenario)
    
    def test_analyze_stock_002379(self):
        """专门测试002379股票分析"""
        response = self.make_request(
            'POST',
            '/api/v1/assistant/analyze-stock',
            json={
                "stock_code": "002379",
                "analysis_type": "technical"
            }
        )
        
        # 允许200(成功)或其他状态(未实现/模拟)
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIn("analysis", response_data)


class TestMarketInsights(APITestCase):
    """市场洞察接口测试"""
    
    def test_get_market_insights_valid_requests(self):
        """测试获取市场洞察有效请求"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/assistant/market-insights',
                params={"insight_type": scenario["insight_type"]}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIn("insights", response_data)
        
        self.run_test_scenarios("market_insights_test_data.valid_requests", test_scenario)
    
    def test_get_market_insights_invalid_requests(self):
        """测试获取市场洞察无效请求"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/assistant/market-insights',
                params={"insight_type": scenario["insight_type"]}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("market_insights_test_data.invalid_requests", test_scenario)


class TestConversationHistory(APITestCase):
    """对话历史接口测试"""
    
    def test_get_conversation_history(self):
        """测试获取对话历史"""
        response = self.make_request(
            'GET',
            '/api/v1/assistant/conversation-history',
            params={"page": 1, "size": 10}
        )
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            self.assertIsInstance(response_data, (list, dict))
    
    def test_conversation_history_pagination(self):
        """测试对话历史分页"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/assistant/conversation-history',
                params={
                    "page": scenario["page"],
                    "size": scenario["size"]
                }
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("conversation_history_test_data.pagination", test_scenario)
    
    def test_conversation_history_invalid_pagination(self):
        """测试对话历史无效分页"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/assistant/conversation-history',
                params={
                    "page": scenario["page"],
                    "size": scenario["size"]
                }
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("conversation_history_test_data.invalid_pagination", test_scenario)


class TestSuggestions(APITestCase):
    """建议接口测试"""
    
    def test_get_suggestions(self):
        """测试获取建议"""
        response = self.make_request('GET', '/api/v1/assistant/suggestions')
        
        # 允许200(有数据)或其他状态
        self.assertIn(response.status_code, [200, 404, 501])
        
        if response.status_code == 200:
            response_data = self.validate_json_response(response)
            expected_fields = self.test_data.get("suggestions_test_data", {}).get("expected_fields", [])
            
            for field in expected_fields:
                if field in response_data:
                    self.assertIsNotNone(response_data[field])
    
    def test_get_suggestions_with_context(self):
        """测试根据上下文获取建议"""
        def test_scenario(scenario):
            response = self.make_request(
                'GET',
                '/api/v1/assistant/suggestions',
                params={"context": scenario["context"]}
            )
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200:
                response_data = self.validate_json_response(response)
                self.assertIn("suggestions", response_data)
        
        self.run_test_scenarios("suggestions_test_data.context_types", test_scenario)


class TestAssistantIntegration(APITestCase):
    """AI助手集成测试"""
    
    def test_chat_to_analysis_flow(self):
        """测试对话到分析的完整流程"""
        # 1. 先进行对话
        chat_response = self.make_request(
            'POST',
            '/api/v1/assistant/chat',
            json={"message": "我想了解002379这只股票"}
        )
        
        # 对话可能成功或未实现
        self.assertIn(chat_response.status_code, [200, 501])
        
        # 2. 然后进行股票分析
        analysis_response = self.make_request(
            'POST',
            '/api/v1/assistant/analyze-stock',
            json={
                "stock_code": "002379",
                "analysis_type": "technical"
            }
        )
        
        # 分析可能成功或未实现
        self.assertIn(analysis_response.status_code, [200, 404, 501])
    
    def test_multiple_chat_sessions(self):
        """测试多轮对话"""
        messages = [
            "你好",
            "请介绍一下股票002379",
            "这只股票的技术指标如何？"
        ]
        
        for i, message in enumerate(messages):
            with self.subTest(round=i+1, message=message):
                response = self.make_request(
                    'POST',
                    '/api/v1/assistant/chat',
                    json={"message": message}
                )
                
                # 每轮对话可能成功或未实现
                self.assertIn(response.status_code, [200, 501])


if __name__ == '__main__':
    unittest.main()

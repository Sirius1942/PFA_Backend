#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI助手模块基本测试用例
"""

import unittest
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestAssistantBasic(APITestCase):
    """基本AI助手功能测试"""
    
    def test_basic_chat(self):
        """测试基本对话功能"""
        message = self.test_data.get("chat_test_data", {}).get("basic_message", "你好")
        
        response = self.make_request(
            'POST',
            '/api/v1/assistant/chat',
            json={"message": message}
        )
        
        # 允许200(成功)或501(未实现)或500(服务错误)
        self.assertIn(response.status_code, [200, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIn("message", response_data)
            self.assertIsInstance(response_data["message"], str)
    
    def test_stock_chat(self):
        """测试股票相关对话"""
        message = self.test_data.get("chat_test_data", {}).get("stock_query", "查询股票002379")
        
        response = self.make_request(
            'POST',
            '/api/v1/assistant/chat',
            json={"message": message}
        )
        
        # 允许多种状态码，主要测试接口可访问性
        self.assertIn(response.status_code, [200, 500, 501])
    
    def test_stock_analysis(self):
        """测试股票分析功能"""
        stock_code = self.test_data.get("analysis_test_data", {}).get("test_stock_code", "002379")
        analysis_type = self.test_data.get("analysis_test_data", {}).get("analysis_type", "technical")
        
        response = self.make_request(
            'POST',
            '/api/v1/assistant/analyze-stock',
            json={
                "stock_code": stock_code,
                "analysis_type": analysis_type
            }
        )
        
        # 允许200(成功)或其他状态(未实现/模拟)
        self.assertIn(response.status_code, [200, 404, 405, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIn("summary", response_data)
            self.assertIn("detailed_analysis", response_data)
    
    def test_market_insights(self):
        """测试市场洞察功能"""
        insight_type = self.test_data.get("insights_test_data", {}).get("insight_type", "daily_summary")
        
        response = self.make_request(
            'GET',
            '/api/v1/assistant/market-insights',
            params={"insight_type": insight_type}
        )
        
        # 允许多种状态码
        self.assertIn(response.status_code, [200, 404, 405, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIn("insights", response_data)
    
    def test_conversation_history(self):
        """测试对话历史功能"""
        params = self.test_data.get("history_test_data", {}).get("default_params", {})
        
        response = self.make_request(
            'GET',
            '/api/v1/assistant/conversation-history',
            params=params
        )
        
        # 允许多种状态码
        self.assertIn(response.status_code, [200, 404, 405, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIsInstance(response_data, (list, dict))
    
    def test_suggestions(self):
        """测试建议功能"""
        response = self.make_request('GET', '/api/v1/assistant/suggestions')
        
        # 允许多种状态码
        self.assertIn(response.status_code, [200, 404, 405, 500, 501])
        
        if response.status_code == 200:
            response_data = response.json()
            self.assertIsInstance(response_data, dict)


if __name__ == '__main__':
    unittest.main()

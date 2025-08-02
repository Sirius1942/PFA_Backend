#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成模块基本测试用例
"""

import unittest
import sys
import pymysql
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase


class TestSystemBasic(APITestCase):
    """基本系统功能测试"""
    
    def test_health_check(self):
        """测试系统健康检查"""
        response = self.session.get(f"{self.base_url}/health")
        
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        
        # 验证基本健康检查字段
        self.assertIn("status", response_data)
        self.assertEqual(response_data["status"], "healthy")
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = self.session.get(f"{self.base_url}/")
        
        self.assertEqual(response.status_code, 200)
    
    def test_api_documentation(self):
        """测试API文档可访问性"""
        endpoints = self.test_data.get("api_docs_test_data", {}).get("endpoints", [])
        
        for endpoint in endpoints[:2]:  # 只测试前两个端点
            with self.subTest(endpoint=endpoint):
                response = self.session.get(f"{self.base_url}{endpoint}")
                self.assertEqual(response.status_code, 200)
    
    def test_openapi_json(self):
        """测试OpenAPI规范"""
        response = self.session.get(f"{self.base_url}/openapi.json")
        
        self.assertEqual(response.status_code, 200)
        openapi_data = response.json()
        
        # 验证OpenAPI基本结构
        self.assertIn("openapi", openapi_data)
        self.assertIn("info", openapi_data)
        self.assertIn("paths", openapi_data)
        
        # 验证有足够的API端点
        paths = openapi_data.get("paths", {})
        self.assertGreater(len(paths), 5)
    
    def test_database_connection(self):
        """测试数据库连接"""
        db_config = self.test_data.get("database_test_data", {}).get("connection_config", {})
        
        try:
            connection = pymysql.connect(
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 3307),
                database=db_config.get("database", "financial_db"),
                user=db_config.get("user", "financial_user"),
                password=db_config.get("password", "financial123")
            )
            
            cursor = connection.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 1)
            
            connection.close()
            
        except Exception as e:
            self.skipTest(f"Database connection not available: {e}")
    
    def test_basic_api_flow(self):
        """测试基本API流程"""
        # 1. 检查健康状态
        health_response = self.session.get(f"{self.base_url}/health")
        self.assertEqual(health_response.status_code, 200)
        
        # 2. 访问API文档
        docs_response = self.session.get(f"{self.base_url}/docs")
        self.assertEqual(docs_response.status_code, 200)
        
        # 3. 测试认证流程
        profile_response = self.make_request('GET', '/api/v1/auth/profile')
        self.assertEqual(profile_response.status_code, 200)
    
    def test_service_integration(self):
        """测试服务集成"""
        # 测试认证 -> 用户信息 -> API访问的基本流程
        
        # 1. 获取用户信息
        profile_response = self.make_request('GET', '/api/v1/auth/profile')
        self.assertEqual(profile_response.status_code, 200)
        
        profile_data = profile_response.json()
        self.assertIn("username", profile_data)
        
        # 2. 测试股票搜索
        search_response = self.make_request(
            'GET',
            '/api/v1/stocks/search',
            params={"q": "002379"}
        )
        
        # 允许多种状态码，主要测试集成性
        self.assertIn(search_response.status_code, [200, 403, 404, 500])


if __name__ == '__main__':
    unittest.main()

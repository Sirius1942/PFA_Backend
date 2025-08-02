#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统集成模块unittest测试用例
"""

import unittest
import sys
import time
import pymysql
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

from tests.base_test import APITestCase, DatabaseTestCase


class TestHealthCheck(APITestCase):
    """健康检查测试"""
    
    def test_health_endpoint(self):
        """测试健康检查端点"""
        def test_scenario(scenario):
            response = self.session.get(f"{self.base_url}{scenario['path']}")
            
            self.assertEqual(response.status_code, scenario["expected_status"])
            
            if response.status_code == 200 and "expected_fields" in scenario:
                response_data = self.validate_json_response(response)
                for field in scenario["expected_fields"]:
                    self.assertIn(field, response_data)
        
        self.run_test_scenarios("health_check_test_data.endpoints", test_scenario)
    
    def test_health_response_structure(self):
        """测试健康检查响应结构"""
        response = self.session.get(f"{self.base_url}/health")
        
        self.assertEqual(response.status_code, 200)
        response_data = self.validate_json_response(response)
        
        # 验证基本健康检查字段
        expected_fields = ["status", "service"]
        for field in expected_fields:
            self.assertIn(field, response_data)
        
        # 验证状态值
        self.assertEqual(response_data["status"], "healthy")
    
    def test_root_endpoint(self):
        """测试根端点"""
        response = self.session.get(f"{self.base_url}/")
        
        self.assertEqual(response.status_code, 200)
    
    def test_health_check_response_time(self):
        """测试健康检查响应时间"""
        start_time = time.time()
        response = self.session.get(f"{self.base_url}/health")
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # 转换为毫秒
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(response_time, 5000, "Health check should respond within 5 seconds")


class TestAPIDocumentation(APITestCase):
    """API文档测试"""
    
    def test_swagger_endpoints(self):
        """测试Swagger端点"""
        def test_scenario(scenario):
            response = self.session.get(f"{self.base_url}{scenario['path']}")
            
            self.assertEqual(response.status_code, scenario["expected_status"])
        
        self.run_test_scenarios("api_documentation_test_data.swagger_endpoints", test_scenario)
    
    def test_openapi_json_structure(self):
        """测试OpenAPI JSON结构"""
        response = self.session.get(f"{self.base_url}/openapi.json")
        
        self.assertEqual(response.status_code, 200)
        openapi_data = self.validate_json_response(response)
        
        # 验证OpenAPI基本结构
        expected_fields = ["openapi", "info", "paths"]
        for field in expected_fields:
            self.assertIn(field, openapi_data)
        
        # 验证API路径数量
        paths = openapi_data.get("paths", {})
        self.assertGreater(len(paths), 10, "Should have more than 10 API endpoints")
    
    def test_docs_accessibility(self):
        """测试文档可访问性"""
        docs_endpoints = ["/docs", "/redoc"]
        
        for endpoint in docs_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.session.get(f"{self.base_url}{endpoint}")
                self.assertEqual(response.status_code, 200)
                self.assertIn("text/html", response.headers.get("content-type", ""))


class TestDatabaseIntegration(DatabaseTestCase):
    """数据库集成测试"""
    
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
            self.fail(f"Database connection failed: {e}")
    
    def test_database_queries(self):
        """测试数据库查询"""
        def test_scenario(scenario):
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
                cursor.execute(scenario["query"])
                result = cursor.fetchone()
                
                if scenario["expected_success"]:
                    self.assertIsNotNone(result)
                
                connection.close()
                
            except Exception as e:
                if scenario["expected_success"]:
                    self.fail(f"Database query failed: {e}")
        
        self.run_test_scenarios("database_test_data.test_queries", test_scenario)
    
    def test_table_existence(self):
        """测试重要表是否存在"""
        db_config = self.test_data.get("database_test_data", {}).get("connection_config", {})
        important_tables = ["users", "stock_info", "kline_data", "roles", "permissions"]
        
        try:
            connection = pymysql.connect(
                host=db_config.get("host", "localhost"),
                port=db_config.get("port", 3307),
                database=db_config.get("database", "financial_db"),
                user=db_config.get("user", "financial_user"),
                password=db_config.get("password", "financial123")
            )
            
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            existing_tables = [table[0] for table in cursor.fetchall()]
            
            for table in important_tables:
                with self.subTest(table=table):
                    self.assertIn(table, existing_tables, f"Table {table} should exist")
            
            connection.close()
            
        except Exception as e:
            self.skipTest(f"Cannot connect to database: {e}")


class TestServiceIntegration(APITestCase):
    """服务集成测试"""
    
    def test_authentication_flow(self):
        """测试认证流程集成"""
        # 1. 登录
        login_response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "admin", "password": "admin123"},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        self.assertEqual(login_response.status_code, 200)
        login_data = login_response.json()
        
        # 2. 使用token访问受保护资源
        token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        profile_response = self.session.get(
            f"{self.base_url}/api/v1/auth/profile",
            headers=headers
        )
        
        self.assertEqual(profile_response.status_code, 200)
    
    def test_stock_data_flow(self):
        """测试股票数据流集成"""
        # 1. 搜索股票
        search_response = self.make_request(
            'GET',
            '/api/v1/stocks/search',
            params={"q": "002379"}
        )
        
        self.assertIn(search_response.status_code, [200, 404])
        
        # 2. 获取股票信息
        info_response = self.make_request('GET', '/api/v1/stocks/info/002379')
        self.assertIn(info_response.status_code, [200, 404])
        
        # 3. 获取实时行情
        realtime_response = self.make_request('GET', '/api/v1/stocks/realtime/002379')
        self.assertIn(realtime_response.status_code, [200, 404])
    
    def test_ai_assistant_flow(self):
        """测试AI助手流集成"""
        # 1. 发送聊天消息
        chat_response = self.make_request(
            'POST',
            '/api/v1/assistant/chat',
            json={"message": "你好"}
        )
        
        self.assertIn(chat_response.status_code, [200, 501])
        
        # 2. 获取对话历史
        history_response = self.make_request(
            'GET',
            '/api/v1/assistant/conversation-history',
            params={"page": 1, "size": 10}
        )
        
        self.assertIn(history_response.status_code, [200, 404, 501])
    
    def test_cross_module_integration(self):
        """测试跨模块集成"""
        # 测试用户认证 -> 股票查询 -> AI分析的完整流程
        
        # 1. 确保已认证
        profile_response = self.make_request('GET', '/api/v1/auth/profile')
        self.assertEqual(profile_response.status_code, 200)
        
        # 2. 查询股票
        stock_response = self.make_request('GET', '/api/v1/stocks/info/002379')
        self.assertIn(stock_response.status_code, [200, 404])
        
        # 3. AI分析股票
        analysis_response = self.make_request(
            'POST',
            '/api/v1/assistant/analyze-stock',
            json={"stock_code": "002379", "analysis_type": "technical"}
        )
        
        self.assertIn(analysis_response.status_code, [200, 404, 501])


class TestPerformance(APITestCase):
    """性能测试"""
    
    def test_api_response_times(self):
        """测试API响应时间"""
        endpoints = [
            "/health",
            "/api/v1/auth/profile",
            "/api/v1/stocks/search?q=002379"
        ]
        
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                start_time = time.time()
                
                if endpoint.startswith("/api/v1") and "auth" not in endpoint:
                    response = self.make_request('GET', endpoint.split('?')[0], 
                                               params={"q": "002379"} if "search" in endpoint else None)
                else:
                    response = self.session.get(f"{self.base_url}{endpoint}")
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                # 允许多种状态码，主要测试响应时间
                self.assertIn(response.status_code, [200, 404, 401])
                self.assertLess(response_time, 10000, f"API {endpoint} should respond within 10 seconds")
    
    def test_concurrent_requests(self):
        """测试并发请求"""
        import threading
        import queue
        
        results = queue.Queue()
        
        def make_health_request():
            try:
                response = self.session.get(f"{self.base_url}/health")
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))
        
        # 创建10个并发请求
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_health_request)
            threads.append(thread)
            thread.start()
        
        # 等待所有线程完成
        for thread in threads:
            thread.join(timeout=10)
        
        # 检查结果
        success_count = 0
        while not results.empty():
            result = results.get()
            if result == 200:
                success_count += 1
        
        # 至少50%的请求应该成功
        self.assertGreaterEqual(success_count, 5, "At least 50% of concurrent requests should succeed")


class TestErrorHandling(APITestCase):
    """错误处理测试"""
    
    def test_404_handling(self):
        """测试404错误处理"""
        response = self.session.get(f"{self.base_url}/nonexistent-endpoint")
        self.assertEqual(response.status_code, 404)
    
    def test_401_handling(self):
        """测试401错误处理"""
        response = self.session.get(f"{self.base_url}/api/v1/auth/profile")
        self.assertEqual(response.status_code, 401)
    
    def test_422_handling(self):
        """测试422错误处理"""
        response = self.session.post(
            f"{self.base_url}/api/v1/auth/login",
            data={"username": "", "password": ""},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        self.assertEqual(response.status_code, 422)


if __name__ == '__main__':
    unittest.main()

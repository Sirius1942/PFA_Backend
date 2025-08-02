#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据采集器

从东方财富网采集股票实时行情和历史数据，存储到SQLite数据库中。

功能：
1. 获取股票列表
2. 采集实时行情数据
3. 采集历史K线数据
4. 数据清洗和标准化
5. 存储到SQLite数据库

作者: Assistant
日期: 2024
"""

import json
import sqlite3
import requests
import pandas as pd
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from pathlib import Path

class EastMoneyDataCollector:
    """
    东方财富网数据采集器
    """
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        初始化数据采集器
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.db_path = self.config['database']['path']
        self.headers = self.config['data_sources']['eastmoney']['headers']
        self.base_url = self.config['data_sources']['eastmoney']['base_url']
        
        # 设置日志
        self._setup_logging()
        
        # 初始化数据库
        self._init_database()
        
        # 股票代码映射
        self.stock_codes = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"配置文件未找到: {config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"配置文件格式错误: {config_path}")
            return {}
    
    def _setup_logging(self):
        """
        设置日志配置
        """
        log_dir = Path("../logs")
        log_dir.mkdir(exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/data_collector.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _init_database(self):
        """
        初始化SQLite数据库
        """
        # 确保数据库目录存在
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建股票基本信息表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_info (
                code TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                market TEXT,
                industry TEXT,
                concept TEXT,
                area TEXT,
                pe_ratio REAL,
                pb_ratio REAL,
                market_cap REAL,
                circulation_cap REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建实时行情表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS realtime_quotes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT,
                current_price REAL,
                change_amount REAL,
                change_percent REAL,
                volume REAL,
                turnover REAL,
                high_price REAL,
                low_price REAL,
                open_price REAL,
                prev_close REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (code) REFERENCES stock_info (code)
            )
        ''')
        
        # 创建历史K线数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS kline_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                date DATE,
                open_price REAL,
                high_price REAL,
                low_price REAL,
                close_price REAL,
                volume REAL,
                turnover REAL,
                change_percent REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(code, date),
                FOREIGN KEY (code) REFERENCES stock_info (code)
            )
        ''')
        
        # 创建技术指标表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS technical_indicators (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                date DATE,
                ma5 REAL,
                ma10 REAL,
                ma20 REAL,
                ma60 REAL,
                macd REAL,
                macd_signal REAL,
                macd_histogram REAL,
                rsi REAL,
                kdj_k REAL,
                kdj_d REAL,
                kdj_j REAL,
                boll_upper REAL,
                boll_middle REAL,
                boll_lower REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(code, date),
                FOREIGN KEY (code) REFERENCES stock_info (code)
            )
        ''')
        
        conn.commit()
        conn.close()
        
        self.logger.info("数据库初始化完成")
    
    def get_stock_list(self, market: str = "A股") -> List[Dict[str, Any]]:
        """
        获取股票列表
        
        Args:
            market: 市场类型 (A股, 港股, 美股)
            
        Returns:
            股票列表
        """
        self.logger.info(f"开始获取{market}股票列表")
        
        # 东方财富A股列表API参数
        params = {
            'cb': 'jQuery112404953340710317169_1629360000000',
            'pn': 1,
            'pz': 5000,  # 获取更多股票
            'po': 1,
            'np': 1,
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股主板+创业板+科创板
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # 解析JSONP响应
            content = response.text
            json_str = re.search(r'\((.*?)\);?$', content).group(1)
            data = json.loads(json_str)
            
            stocks = []
            if data.get('data') and data['data'].get('diff'):
                for item in data['data']['diff']:
                    stock = {
                        'code': item.get('f12', ''),  # 股票代码
                        'name': item.get('f14', ''),  # 股票名称
                        'current_price': item.get('f2', 0),  # 当前价格
                        'change_percent': item.get('f3', 0),  # 涨跌幅
                        'change_amount': item.get('f4', 0),  # 涨跌额
                        'volume': item.get('f5', 0),  # 成交量
                        'turnover': item.get('f6', 0),  # 成交额
                        'high_price': item.get('f15', 0),  # 最高价
                        'low_price': item.get('f16', 0),  # 最低价
                        'open_price': item.get('f17', 0),  # 开盘价
                        'prev_close': item.get('f18', 0),  # 昨收价
                        'pe_ratio': item.get('f9', 0),  # 市盈率
                        'pb_ratio': item.get('f23', 0),  # 市净率
                        'market_cap': item.get('f20', 0),  # 总市值
                        'circulation_cap': item.get('f21', 0),  # 流通市值
                        'market': self._get_market_by_code(item.get('f12', ''))
                    }
                    stocks.append(stock)
            
            self.logger.info(f"成功获取{len(stocks)}只股票数据")
            return stocks
            
        except Exception as e:
            self.logger.error(f"获取股票列表失败: {e}")
            return []
    
    def _get_market_by_code(self, code: str) -> str:
        """
        根据股票代码判断所属市场
        
        Args:
            code: 股票代码
            
        Returns:
            市场名称
        """
        if code.startswith('6'):
            return '上海主板'
        elif code.startswith('00'):
            return '深圳主板'
        elif code.startswith('30'):
            return '创业板'
        elif code.startswith('68'):
            return '科创板'
        elif code.startswith('8') or code.startswith('4'):
            return '北交所'
        else:
            return '其他'
    
    def save_stock_list(self, stocks: List[Dict[str, Any]]) -> bool:
        """
        保存股票列表到数据库
        
        Args:
            stocks: 股票列表
            
        Returns:
            是否保存成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for stock in stocks:
                # 更新或插入股票基本信息
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_info 
                    (code, name, market, pe_ratio, pb_ratio, market_cap, circulation_cap, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock['code'],
                    stock['name'],
                    stock['market'],
                    stock['pe_ratio'],
                    stock['pb_ratio'],
                    stock['market_cap'],
                    stock['circulation_cap'],
                    datetime.now()
                ))
                
                # 插入实时行情数据
                cursor.execute('''
                    INSERT INTO realtime_quotes 
                    (code, name, current_price, change_amount, change_percent, 
                     volume, turnover, high_price, low_price, open_price, prev_close)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    stock['code'],
                    stock['name'],
                    stock['current_price'],
                    stock['change_amount'],
                    stock['change_percent'],
                    stock['volume'],
                    stock['turnover'],
                    stock['high_price'],
                    stock['low_price'],
                    stock['open_price'],
                    stock['prev_close']
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"成功保存{len(stocks)}只股票数据到数据库")
            return True
            
        except Exception as e:
            self.logger.error(f"保存股票数据失败: {e}")
            return False
    
    def get_historical_data(self, stock_code: str, period: str = "daily", 
                          start_date: str = None, end_date: str = None) -> List[Dict[str, Any]]:
        """
        获取股票历史数据
        
        Args:
            stock_code: 股票代码
            period: 周期 (daily, weekly, monthly)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            历史数据列表
        """
        self.logger.info(f"开始获取{stock_code}的历史数据")
        
        # 构建历史数据API URL
        # 这里使用东方财富的历史数据接口
        market_code = "1" if stock_code.startswith('6') else "0"
        secid = f"{market_code}.{stock_code}"
        
        # 默认获取最近一年的数据
        if not end_date:
            end_date = datetime.now().strftime('%Y%m%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
        
        url = "http://push2his.eastmoney.com/api/qt/stock/kline/get"
        params = {
            'cb': 'jQuery112404953340710317169_1629360000000',
            'secid': secid,
            'ut': 'fa5fd1943c7b386f172d6893dbfba10b',
            'fields1': 'f1,f2,f3,f4,f5,f6',
            'fields2': 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
            'klt': '101',  # 日K线
            'fqt': '1',    # 前复权
            'beg': start_date,
            'end': end_date,
            '_': str(int(time.time() * 1000))
        }
        
        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            # 解析JSONP响应
            content = response.text
            json_str = re.search(r'\((.*?)\);?$', content).group(1)
            data = json.loads(json_str)
            
            klines = []
            if data.get('data') and data['data'].get('klines'):
                for kline_str in data['data']['klines']:
                    parts = kline_str.split(',')
                    if len(parts) >= 11:
                        kline = {
                            'code': stock_code,
                            'date': parts[0],
                            'open_price': float(parts[1]),
                            'close_price': float(parts[2]),
                            'high_price': float(parts[3]),
                            'low_price': float(parts[4]),
                            'volume': float(parts[5]),
                            'turnover': float(parts[6]),
                            'change_percent': float(parts[8])
                        }
                        klines.append(kline)
            
            self.logger.info(f"成功获取{stock_code}的{len(klines)}条历史数据")
            return klines
            
        except Exception as e:
            self.logger.error(f"获取{stock_code}历史数据失败: {e}")
            return []
    
    def save_historical_data(self, klines: List[Dict[str, Any]]) -> bool:
        """
        保存历史数据到数据库
        
        Args:
            klines: K线数据列表
            
        Returns:
            是否保存成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for kline in klines:
                cursor.execute('''
                    INSERT OR REPLACE INTO kline_data 
                    (code, date, open_price, high_price, low_price, close_price, 
                     volume, turnover, change_percent)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    kline['code'],
                    kline['date'],
                    kline['open_price'],
                    kline['high_price'],
                    kline['low_price'],
                    kline['close_price'],
                    kline['volume'],
                    kline['turnover'],
                    kline['change_percent']
                ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"成功保存{len(klines)}条历史数据到数据库")
            return True
            
        except Exception as e:
            self.logger.error(f"保存历史数据失败: {e}")
            return False
    
    def collect_all_data(self, limit: int = 100):
        """
        采集所有股票数据
        
        Args:
            limit: 限制采集的股票数量
        """
        self.logger.info("开始采集所有股票数据")
        
        # 1. 获取股票列表
        stocks = self.get_stock_list()
        if not stocks:
            self.logger.error("获取股票列表失败")
            return
        
        # 限制采集数量
        if limit and len(stocks) > limit:
            stocks = stocks[:limit]
        
        # 2. 保存股票列表和实时行情
        self.save_stock_list(stocks)
        
        # 3. 采集历史数据（仅采集前50只股票的历史数据，避免请求过多）
        for i, stock in enumerate(stocks[:50]):
            self.logger.info(f"采集{stock['code']} {stock['name']}的历史数据 ({i+1}/50)")
            
            historical_data = self.get_historical_data(stock['code'])
            if historical_data:
                self.save_historical_data(historical_data)
            
            # 添加延时，避免请求过于频繁
            time.sleep(1)
        
        self.logger.info("数据采集完成")

def main():
    """
    主函数
    """
    print("🚀 股票数据采集器")
    print("=" * 50)
    
    collector = EastMoneyDataCollector()
    
    print("选择采集模式:")
    print("1. 采集股票列表和实时行情")
    print("2. 采集指定股票的历史数据")
    print("3. 采集所有数据（限制100只股票）")
    
    choice = input("\n请选择 (1/2/3): ").strip()
    
    if choice == '1':
        stocks = collector.get_stock_list()
        if stocks:
            collector.save_stock_list(stocks)
            print(f"✅ 成功采集{len(stocks)}只股票的实时行情")
        else:
            print("❌ 采集失败")
    
    elif choice == '2':
        stock_code = input("请输入股票代码 (如: 000001): ").strip()
        if stock_code:
            historical_data = collector.get_historical_data(stock_code)
            if historical_data:
                collector.save_historical_data(historical_data)
                print(f"✅ 成功采集{stock_code}的{len(historical_data)}条历史数据")
            else:
                print("❌ 采集失败")
    
    elif choice == '3':
        collector.collect_all_data(limit=100)
        print("✅ 数据采集完成")
    
    else:
        print("❌ 无效选择")

if __name__ == "__main__":
    main()
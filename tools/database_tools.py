#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库查询工具

为金融量化分析Agent提供股票数据查询功能。

功能：
1. 股票基本信息查询
2. 实时行情查询
3. 历史K线数据查询
4. 技术指标查询
5. 市场统计分析

作者: Assistant
日期: 2024
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path

class StockDatabaseTools:
    """
    股票数据库查询工具类
    """
    
    def __init__(self, db_path: str = "database/stock_data.db"):
        """
        初始化数据库工具
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """
        确保数据库文件存在
        """
        if not Path(self.db_path).exists():
            print(f"⚠️ 数据库文件不存在: {self.db_path}")
            print("请先运行数据采集器创建数据库")
    
    def get_stock_info(self, code: str = None, name: str = None) -> List[Dict[str, Any]]:
        """
        查询股票基本信息
        
        Args:
            code: 股票代码
            name: 股票名称（支持模糊查询）
            
        Returns:
            股票信息列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if code:
                query = "SELECT * FROM stock_info WHERE code = ?"
                df = pd.read_sql_query(query, conn, params=[code])
            elif name:
                query = "SELECT * FROM stock_info WHERE name LIKE ?"
                df = pd.read_sql_query(query, conn, params=[f"%{name}%"])
            else:
                query = "SELECT * FROM stock_info LIMIT 50"
                df = pd.read_sql_query(query, conn)
            
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            print(f"查询股票信息失败: {e}")
            return []
    
    def get_realtime_quotes(self, code: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        查询实时行情数据
        
        Args:
            code: 股票代码
            limit: 返回记录数限制
            
        Returns:
            实时行情列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if code:
                query = """
                    SELECT * FROM realtime_quotes 
                    WHERE code = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=[code, limit])
            else:
                query = """
                    SELECT * FROM realtime_quotes 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=[limit])
            
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            print(f"查询实时行情失败: {e}")
            return []
    
    def get_kline_data(self, code: str, start_date: str = None, 
                      end_date: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        查询K线历史数据
        
        Args:
            code: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            limit: 返回记录数限制
            
        Returns:
            K线数据列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if start_date and end_date:
                query = """
                    SELECT * FROM kline_data 
                    WHERE code = ? AND date BETWEEN ? AND ?
                    ORDER BY date DESC 
                    LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=[code, start_date, end_date, limit])
            else:
                query = """
                    SELECT * FROM kline_data 
                    WHERE code = ? 
                    ORDER BY date DESC 
                    LIMIT ?
                """
                df = pd.read_sql_query(query, conn, params=[code, limit])
            
            conn.close()
            return df.to_dict('records')
            
        except Exception as e:
            print(f"查询K线数据失败: {e}")
            return []
    
    def get_market_overview(self) -> Dict[str, Any]:
        """
        获取市场概览统计
        
        Returns:
            市场统计信息
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            # 统计各市场股票数量
            market_stats = pd.read_sql_query("""
                SELECT market, COUNT(*) as count
                FROM stock_info 
                GROUP BY market
            """, conn)
            
            # 涨跌统计
            price_stats = pd.read_sql_query("""
                SELECT 
                    COUNT(CASE WHEN change_percent > 0 THEN 1 END) as rising_count,
                    COUNT(CASE WHEN change_percent < 0 THEN 1 END) as falling_count,
                    COUNT(CASE WHEN change_percent = 0 THEN 1 END) as flat_count,
                    AVG(change_percent) as avg_change_percent,
                    MAX(change_percent) as max_change_percent,
                    MIN(change_percent) as min_change_percent
                FROM realtime_quotes 
                WHERE timestamp >= datetime('now', '-1 day')
            """, conn)
            
            # 成交量统计
            volume_stats = pd.read_sql_query("""
                SELECT 
                    SUM(volume) as total_volume,
                    SUM(turnover) as total_turnover,
                    AVG(volume) as avg_volume,
                    AVG(turnover) as avg_turnover
                FROM realtime_quotes 
                WHERE timestamp >= datetime('now', '-1 day')
            """, conn)
            
            conn.close()
            
            return {
                'market_distribution': market_stats.to_dict('records'),
                'price_statistics': price_stats.to_dict('records')[0] if not price_stats.empty else {},
                'volume_statistics': volume_stats.to_dict('records')[0] if not volume_stats.empty else {},
                'update_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"获取市场概览失败: {e}")
            return {}
    
    def search_stocks(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索股票（支持代码和名称）
        
        Args:
            keyword: 搜索关键词
            limit: 返回记录数限制
            
        Returns:
            匹配的股票列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = """
                SELECT s.*, r.current_price, r.change_percent, r.timestamp
                FROM stock_info s
                LEFT JOIN (
                    SELECT code, current_price, change_percent, timestamp,
                           ROW_NUMBER() OVER (PARTITION BY code ORDER BY timestamp DESC) as rn
                    FROM realtime_quotes
                ) r ON s.code = r.code AND r.rn = 1
                WHERE s.code LIKE ? OR s.name LIKE ?
                ORDER BY s.market_cap DESC
                LIMIT ?
            """
            
            df = pd.read_sql_query(query, conn, params=[f"%{keyword}%", f"%{keyword}%", limit])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"搜索股票失败: {e}")
            return []
    
    def get_top_performers(self, metric: str = "change_percent", 
                          limit: int = 10, ascending: bool = False) -> List[Dict[str, Any]]:
        """
        获取表现最佳/最差的股票
        
        Args:
            metric: 排序指标 (change_percent, volume, turnover, market_cap)
            limit: 返回记录数限制
            ascending: 是否升序排列
            
        Returns:
            股票排行列表
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            if metric in ['change_percent', 'volume', 'turnover']:
                # 从实时行情表查询
                order = "ASC" if ascending else "DESC"
                query = f"""
                    SELECT r.*, s.name, s.market
                    FROM realtime_quotes r
                    JOIN stock_info s ON r.code = s.code
                    WHERE r.timestamp >= datetime('now', '-1 day')
                    ORDER BY r.{metric} {order}
                    LIMIT ?
                """
            else:
                # 从股票信息表查询
                order = "ASC" if ascending else "DESC"
                query = f"""
                    SELECT s.*, r.current_price, r.change_percent
                    FROM stock_info s
                    LEFT JOIN (
                        SELECT code, current_price, change_percent,
                               ROW_NUMBER() OVER (PARTITION BY code ORDER BY timestamp DESC) as rn
                        FROM realtime_quotes
                    ) r ON s.code = r.code AND r.rn = 1
                    ORDER BY s.{metric} {order}
                    LIMIT ?
                """
            
            df = pd.read_sql_query(query, conn, params=[limit])
            conn.close()
            
            return df.to_dict('records')
            
        except Exception as e:
            print(f"获取排行榜失败: {e}")
            return []
    
    def get_stock_analysis(self, code: str) -> Dict[str, Any]:
        """
        获取股票分析数据
        
        Args:
            code: 股票代码
            
        Returns:
            股票分析结果
        """
        try:
            # 基本信息
            stock_info = self.get_stock_info(code=code)
            if not stock_info:
                return {'error': f'未找到股票代码: {code}'}
            
            # 最新行情
            latest_quote = self.get_realtime_quotes(code=code, limit=1)
            
            # 历史数据（最近30天）
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            kline_data = self.get_kline_data(code, start_date, end_date, limit=30)
            
            # 计算简单技术指标
            analysis = {
                'basic_info': stock_info[0],
                'latest_quote': latest_quote[0] if latest_quote else {},
                'historical_data': kline_data,
                'technical_analysis': self._calculate_technical_indicators(kline_data),
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return analysis
            
        except Exception as e:
            print(f"获取股票分析失败: {e}")
            return {'error': str(e)}
    
    def _calculate_technical_indicators(self, kline_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算技术指标
        
        Args:
            kline_data: K线数据
            
        Returns:
            技术指标字典
        """
        if not kline_data or len(kline_data) < 5:
            return {}
        
        try:
            df = pd.DataFrame(kline_data)
            df = df.sort_values('date')
            
            # 计算移动平均线
            df['ma5'] = df['close_price'].rolling(window=5).mean()
            df['ma10'] = df['close_price'].rolling(window=10).mean()
            df['ma20'] = df['close_price'].rolling(window=20).mean()
            
            # 计算RSI
            delta = df['close_price'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['rsi'] = 100 - (100 / (1 + rs))
            
            # 获取最新值
            latest = df.iloc[-1]
            
            return {
                'ma5': round(latest.get('ma5', 0), 2),
                'ma10': round(latest.get('ma10', 0), 2),
                'ma20': round(latest.get('ma20', 0), 2),
                'rsi': round(latest.get('rsi', 0), 2),
                'price_trend': self._analyze_price_trend(df),
                'volume_trend': self._analyze_volume_trend(df)
            }
            
        except Exception as e:
            print(f"计算技术指标失败: {e}")
            return {}
    
    def _analyze_price_trend(self, df: pd.DataFrame) -> str:
        """
        分析价格趋势
        
        Args:
            df: 股票数据DataFrame
            
        Returns:
            趋势描述
        """
        if len(df) < 5:
            return "数据不足"
        
        recent_prices = df['close_price'].tail(5).tolist()
        
        if recent_prices[-1] > recent_prices[0]:
            return "上涨趋势"
        elif recent_prices[-1] < recent_prices[0]:
            return "下跌趋势"
        else:
            return "横盘整理"
    
    def _analyze_volume_trend(self, df: pd.DataFrame) -> str:
        """
        分析成交量趋势
        
        Args:
            df: 股票数据DataFrame
            
        Returns:
            成交量趋势描述
        """
        if len(df) < 5:
            return "数据不足"
        
        recent_volumes = df['volume'].tail(5).tolist()
        avg_volume = sum(recent_volumes) / len(recent_volumes)
        latest_volume = recent_volumes[-1]
        
        if latest_volume > avg_volume * 1.5:
            return "放量"
        elif latest_volume < avg_volume * 0.5:
            return "缩量"
        else:
            return "正常"
    
    def export_data(self, table_name: str, output_path: str, 
                   conditions: str = None) -> bool:
        """
        导出数据到CSV文件
        
        Args:
            table_name: 表名
            output_path: 输出文件路径
            conditions: SQL WHERE条件
            
        Returns:
            是否导出成功
        """
        try:
            conn = sqlite3.connect(self.db_path)
            
            query = f"SELECT * FROM {table_name}"
            if conditions:
                query += f" WHERE {conditions}"
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            print(f"✅ 数据已导出到: {output_path}")
            return True
            
        except Exception as e:
            print(f"导出数据失败: {e}")
            return False

def main():
    """
    测试数据库工具功能
    """
    print("🔍 股票数据库查询工具测试")
    print("=" * 50)
    
    db_tools = StockDatabaseTools()
    
    # 测试搜索功能
    print("\n1. 搜索股票测试:")
    results = db_tools.search_stocks("平安", limit=5)
    for stock in results:
        print(f"  {stock.get('code', 'N/A')} {stock.get('name', 'N/A')} - 当前价: {stock.get('current_price', 'N/A')}")
    
    # 测试市场概览
    print("\n2. 市场概览:")
    overview = db_tools.get_market_overview()
    if overview:
        print(f"  更新时间: {overview.get('update_time', 'N/A')}")
        if 'price_statistics' in overview:
            stats = overview['price_statistics']
            print(f"  上涨股票: {stats.get('rising_count', 0)}")
            print(f"  下跌股票: {stats.get('falling_count', 0)}")
            print(f"  平均涨跌幅: {stats.get('avg_change_percent', 0):.2f}%")
    
    # 测试排行榜
    print("\n3. 涨幅排行榜 (前5名):")
    top_gainers = db_tools.get_top_performers("change_percent", limit=5)
    for i, stock in enumerate(top_gainers, 1):
        print(f"  {i}. {stock.get('code', 'N/A')} {stock.get('name', 'N/A')} - 涨幅: {stock.get('change_percent', 0):.2f}%")

if __name__ == "__main__":
    main()
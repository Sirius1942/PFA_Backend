#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据计算工具

使用pandas进行股票数据的各种计算，包括涨跌幅、技术指标等。

作者: Assistant
日期: 2024
"""

import pandas as pd
import numpy as np
import sqlite3
from typing import Dict, List, Any, Optional
from pathlib import Path
import tempfile
import os

class DataCalculator:
    """
    数据计算工具类
    使用pandas进行各种股票数据计算
    """
    
    def __init__(self, db_path: str = "database/stock_data.db"):
        """
        初始化数据计算器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
    
    def create_temp_script(self, script_content: str) -> str:
        """
        创建临时计算脚本
        
        Args:
            script_content: 脚本内容
            
        Returns:
            临时脚本文件路径
        """
        temp_dir = Path("temp_scripts")
        temp_dir.mkdir(exist_ok=True)
        
        temp_file = temp_dir / f"calc_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.py"
        
        with open(temp_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        return str(temp_file)
    
    def run_temp_script(self, script_path: str) -> str:
        """
        运行临时脚本并返回结果
        
        Args:
            script_path: 脚本文件路径
            
        Returns:
            脚本执行结果
        """
        import subprocess
        import sys
        
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                cwd=Path(script_path).parent.parent
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return f"脚本执行错误: {result.stderr}"
        except Exception as e:
            return f"执行脚本时出错: {str(e)}"
    
    def cleanup_temp_script(self, script_path: str):
        """
        清理临时脚本文件
        
        Args:
            script_path: 脚本文件路径
        """
        try:
            if os.path.exists(script_path):
                os.remove(script_path)
        except Exception as e:
            print(f"清理临时文件失败: {e}")
    
    def fix_realtime_quotes_calculation(self, code: str) -> str:
        """
        修复实时行情的涨跌幅计算
        
        Args:
            code: 股票代码
            
        Returns:
            修复结果
        """
        script_content = f'''
import sqlite3
import pandas as pd
import numpy as np

# 连接数据库
conn = sqlite3.connect('{self.db_path}')

try:
    # 获取{code}的最新K线数据
    kline_query = """
        SELECT * FROM kline_data 
        WHERE code = '{code}' 
        ORDER BY date DESC 
        LIMIT 2
    """
    kline_df = pd.read_sql_query(kline_query, conn)
    
    if len(kline_df) < 2:
        print(f"数据不足，无法计算{code}的涨跌幅")
    else:
        # 获取最新和前一日的收盘价
        latest_close = kline_df.iloc[0]['close_price']
        prev_close = kline_df.iloc[1]['close_price']
        
        # 计算涨跌额和涨跌幅
        change_amount = latest_close - prev_close
        change_percent = (change_amount / prev_close) * 100
        
        print(f"股票代码: {code}")
        print(f"最新收盘价: {{latest_close}}")
        print(f"前日收盘价: {{prev_close}}")
        print(f"涨跌额: {{change_amount:.4f}}")
        print(f"涨跌幅: {{change_percent:.2f}}%")
        
        # 更新实时行情数据
        update_query = """
            UPDATE realtime_quotes 
            SET 
                current_price = ?,
                change_amount = ?,
                change_percent = ?,
                prev_close = ?
            WHERE code = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(update_query, (
            latest_close,
            change_amount,
            change_percent,
            prev_close,
            code
        ))
        conn.commit()
        
        print(f"\\n已更新{code}的实时行情数据")
        
        # 验证更新结果
        verify_query = "SELECT * FROM realtime_quotes WHERE code = ?"
        verify_df = pd.read_sql_query(verify_query, conn, params=[code])
        print("\\n更新后的数据:")
        print(verify_df[['code', 'current_price', 'change_amount', 'change_percent', 'prev_close']].to_string())
        
except Exception as e:
    print(f"计算过程中出错: {{e}}")
finally:
    conn.close()
'''
        
        # 创建并运行临时脚本
        script_path = self.create_temp_script(script_content)
        result = self.run_temp_script(script_path)
        self.cleanup_temp_script(script_path)
        
        return result
    
    def calculate_technical_indicators(self, code: str, period: int = 20) -> str:
        """
        计算技术指标
        
        Args:
            code: 股票代码
            period: 计算周期
            
        Returns:
            计算结果
        """
        script_content = f'''
import sqlite3
import pandas as pd
import numpy as np

# 连接数据库
conn = sqlite3.connect('{self.db_path}')

try:
    # 获取历史数据
    query = """
        SELECT date, close_price, high_price, low_price, volume
        FROM kline_data 
        WHERE code = '{code}' 
        ORDER BY date DESC 
        LIMIT 100
    """
    df = pd.read_sql_query(query, conn)
    df = df.sort_values('date').reset_index(drop=True)
    
    if len(df) < {period}:
        print(f"数据不足，需要至少{period}条记录")
    else:
        # 计算移动平均线
        df['MA5'] = df['close_price'].rolling(window=5).mean()
        df['MA10'] = df['close_price'].rolling(window=10).mean()
        df['MA20'] = df['close_price'].rolling(window=20).mean()
        
        # 计算RSI
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 计算MACD
        exp1 = df['close_price'].ewm(span=12).mean()
        exp2 = df['close_price'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        df['Signal'] = df['MACD'].ewm(span=9).mean()
        df['Histogram'] = df['MACD'] - df['Signal']
        
        # 显示最新的技术指标
        latest = df.iloc[-1]
        print(f"股票代码: {code}")
        print(f"日期: {latest['date']}")
        print(f"收盘价: {latest['close_price']:.2f}")
        print(f"MA5: {latest['MA5']:.2f}")
        print(f"MA10: {latest['MA10']:.2f}")
        print(f"MA20: {latest['MA20']:.2f}")
        print(f"RSI: {latest['RSI']:.2f}")
        print(f"MACD: {latest['MACD']:.4f}")
        print(f"Signal: {latest['Signal']:.4f}")
        print(f"Histogram: {latest['Histogram']:.4f}")
        
except Exception as e:
    print(f"计算技术指标时出错: {e}")
finally:
    conn.close()
'''
        
        # 创建并运行临时脚本
        script_path = self.create_temp_script(script_content)
        result = self.run_temp_script(script_path)
        self.cleanup_temp_script(script_path)
        
        return result
    
    def calculate_custom_metrics(self, code: str, calculation_type: str, **kwargs) -> str:
        """
        执行自定义计算
        
        Args:
            code: 股票代码
            calculation_type: 计算类型
            **kwargs: 其他参数
            
        Returns:
            计算结果
        """
        if calculation_type == "price_change":
            return self.fix_realtime_quotes_calculation(code)
        elif calculation_type == "technical_indicators":
            period = kwargs.get('period', 20)
            return self.calculate_technical_indicators(code, period)
        else:
            return f"不支持的计算类型: {calculation_type}"
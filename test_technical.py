#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd
import numpy as np

# 连接数据库
conn = sqlite3.connect('database/stock_data.db')

try:
    # 获取历史数据
    query = """
        SELECT date, close_price, high_price, low_price, volume
        FROM kline_data 
        WHERE code = '002379' 
        ORDER BY date DESC 
        LIMIT 100
    """
    df = pd.read_sql_query(query, conn)
    df = df.sort_values('date').reset_index(drop=True)
    
    if len(df) < 20:
        print(f"数据不足，需要至少20条记录")
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
        print(f"股票代码: 002379")
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
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

# 连接数据库
conn = sqlite3.connect('database/stock_data.db')

try:
    # 获取002379的最新K线数据
    kline_query = """
        SELECT * FROM kline_data 
        WHERE code = '002379' 
        ORDER BY date DESC 
        LIMIT 2
    """
    kline_df = pd.read_sql_query(kline_query, conn)
    
    if len(kline_df) < 2:
        print("数据不足，无法计算002379的涨跌幅")
    else:
        # 获取最新和前一日的收盘价
        latest_close = kline_df.iloc[0]['close_price']
        prev_close = kline_df.iloc[1]['close_price']
        
        # 计算涨跌额和涨跌幅
        change_amount = latest_close - prev_close
        change_percent = (change_amount / prev_close) * 100
        
        print(f"股票代码: 002379")
        print(f"最新收盘价: {latest_close}")
        print(f"前日收盘价: {prev_close}")
        print(f"涨跌额: {change_amount:.4f}")
        print(f"涨跌幅: {change_percent:.2f}%")
        
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
            '002379'
        ))
        conn.commit()
        
        print(f"\n已更新002379的实时行情数据")
        
        # 验证更新结果
        verify_query = "SELECT * FROM realtime_quotes WHERE code = ?"
        verify_df = pd.read_sql_query(verify_query, conn, params=['002379'])
        print("\n更新后的数据:")
        print(verify_df[['code', 'current_price', 'change_amount', 'change_percent', 'prev_close']].to_string())
        
except Exception as e:
    print(f"计算过程中出错: {e}")
finally:
    conn.close()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import pandas as pd

# 连接数据库
conn = sqlite3.connect('database/stock_data.db')

try:
    # 获取002379的最新K线数据来重建正确的实时行情
    kline_query = """
        SELECT * FROM kline_data 
        WHERE code = '002379' 
        ORDER BY date DESC 
        LIMIT 1
    """
    kline_df = pd.read_sql_query(kline_query, conn)
    
    if len(kline_df) == 0:
        print("未找到002379的K线数据")
    else:
        latest_data = kline_df.iloc[0]
        
        # 从K线数据获取正确的值
        current_price = latest_data['close_price']  # 当前价 = 收盘价
        open_price = latest_data['open_price']      # 开盘价
        high_price = latest_data['high_price']      # 最高价
        low_price = latest_data['low_price']        # 最低价
        volume = latest_data['volume']              # 成交量
        turnover = latest_data['turnover']          # 成交额
        
        # 计算涨跌额和涨跌幅（已经在之前的脚本中计算过）
        # 获取当前的涨跌数据
        current_query = "SELECT change_amount, change_percent, prev_close FROM realtime_quotes WHERE code = '002379'"
        current_df = pd.read_sql_query(current_query, conn)
        
        if len(current_df) > 0:
            change_amount = current_df.iloc[0]['change_amount']
            change_percent = current_df.iloc[0]['change_percent']
            prev_close = current_df.iloc[0]['prev_close']
        else:
            # 如果没有数据，使用默认值
            change_amount = 0
            change_percent = 0
            prev_close = current_price
        
        print(f"修复002379实时行情数据:")
        print(f"当前价: {current_price}")
        print(f"开盘价: {open_price}")
        print(f"最高价: {high_price}")
        print(f"最低价: {low_price}")
        print(f"成交量: {volume}")
        print(f"成交额: {turnover}")
        print(f"涨跌额: {change_amount:.4f}")
        print(f"涨跌幅: {change_percent:.2f}%")
        
        # 更新实时行情数据
        update_query = """
            UPDATE realtime_quotes 
            SET 
                current_price = ?,
                open_price = ?,
                high_price = ?,
                low_price = ?,
                volume = ?,
                turnover = ?,
                change_amount = ?,
                change_percent = ?,
                prev_close = ?
            WHERE code = ?
        """
        
        cursor = conn.cursor()
        cursor.execute(update_query, (
            current_price,
            open_price,
            high_price,
            low_price,
            volume,
            turnover,
            change_amount,
            change_percent,
            prev_close,
            '002379'
        ))
        conn.commit()
        
        print(f"\n已修复002379的实时行情数据")
        
        # 验证修复结果
        verify_query = "SELECT * FROM realtime_quotes WHERE code = ?"
        verify_df = pd.read_sql_query(verify_query, conn, params=['002379'])
        print("\n修复后的完整数据:")
        for col in verify_df.columns:
            if col != 'id':
                print(f"{col}: {verify_df.iloc[0][col]}")
        
except Exception as e:
    print(f"修复过程中出错: {e}")
finally:
    conn.close()
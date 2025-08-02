#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为002379添加实时行情数据
"""

import sqlite3
from datetime import datetime

def add_realtime_data():
    """
    为002379添加实时行情数据
    """
    conn = sqlite3.connect('database/stock_data.db')
    cursor = conn.cursor()
    
    # 获取最新的历史数据
    cursor.execute('SELECT * FROM kline_data WHERE code = ? ORDER BY date DESC LIMIT 1', ('002379',))
    latest = cursor.fetchone()
    
    if latest:
        # 基于最新历史数据创建实时行情
        code = latest[1]
        close_price = latest[5]  # 收盘价
        open_price = latest[2]   # 开盘价
        high_price = latest[3]   # 最高价
        low_price = latest[4]    # 最低价
        volume = latest[6]       # 成交量
        turnover = latest[7]     # 成交额
        change_percent = latest[8]  # 涨跌幅
        
        # 计算涨跌额
        prev_close = close_price / (1 + change_percent / 100)
        change_amount = close_price - prev_close
        
        # 插入实时行情数据
        cursor.execute('''
            INSERT INTO realtime_quotes 
            (code, name, current_price, change_amount, change_percent, 
             volume, turnover, high_price, low_price, open_price, prev_close, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            code, '宏创控股', close_price, change_amount, change_percent,
            volume, turnover, high_price, low_price, open_price, prev_close,
            datetime.now()
        ))
        
        conn.commit()
        print(f'✅ 已为{code}添加实时行情数据')
        print(f'   当前价: {close_price}')
        print(f'   涨跌幅: {change_percent}%')
        print(f'   成交量: {volume}')
        
    else:
        print('❌ 未找到002379的历史数据')
    
    conn.close()

if __name__ == '__main__':
    add_realtime_data()
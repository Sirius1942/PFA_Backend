#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, Index
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class StockInfo(Base):
    """股票基本信息模型"""
    __tablename__ = "stock_info"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, index=True, nullable=False, comment="股票代码")
    name = Column(String(100), nullable=False, comment="股票名称")
    market = Column(String(10), nullable=False, comment="市场类型(SH/SZ)")
    industry = Column(String(100), nullable=True, comment="所属行业")
    sector = Column(String(100), nullable=True, comment="所属板块")
    listing_date = Column(DateTime, nullable=True, comment="上市日期")
    
    # 基本财务信息
    total_shares = Column(Float, nullable=True, comment="总股本")
    float_shares = Column(Float, nullable=True, comment="流通股本")
    market_cap = Column(Float, nullable=True, comment="总市值")
    float_market_cap = Column(Float, nullable=True, comment="流通市值")
    
    # 状态字段
    is_active = Column(Boolean, default=True, comment="是否有效")
    is_st = Column(Boolean, default=False, comment="是否ST股票")
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<StockInfo(code='{self.code}', name='{self.name}', market='{self.market}')>"

class KlineData(Base):
    """K线数据模型"""
    __tablename__ = "kline_data"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), index=True, nullable=False, comment="股票代码")
    date = Column(DateTime, index=True, nullable=False, comment="交易日期")
    
    # OHLCV数据
    open_price = Column(Float, nullable=False, comment="开盘价")
    high_price = Column(Float, nullable=False, comment="最高价")
    low_price = Column(Float, nullable=False, comment="最低价")
    close_price = Column(Float, nullable=False, comment="收盘价")
    volume = Column(Float, nullable=False, comment="成交量")
    amount = Column(Float, nullable=False, comment="成交额")
    
    # 涨跌信息
    change_amount = Column(Float, nullable=True, comment="涨跌额")
    change_percent = Column(Float, nullable=True, comment="涨跌幅")
    
    # 技术指标
    turnover_rate = Column(Float, nullable=True, comment="换手率")
    
    # 复权信息
    adj_factor = Column(Float, default=1.0, comment="复权因子")
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_code_date', 'code', 'date'),
        Index('idx_date_code', 'date', 'code'),
    )
    
    def __repr__(self):
        return f"<KlineData(code='{self.code}', date='{self.date}', close={self.close_price})>"

class RealtimeQuotes(Base):
    """实时行情模型"""
    __tablename__ = "realtime_quotes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), index=True, nullable=False, comment="股票代码")
    name = Column(String(100), nullable=False, comment="股票名称")
    
    # 价格信息
    current_price = Column(Float, nullable=False, comment="当前价格")
    open_price = Column(Float, nullable=False, comment="开盘价")
    high_price = Column(Float, nullable=False, comment="最高价")
    low_price = Column(Float, nullable=False, comment="最低价")
    pre_close = Column(Float, nullable=False, comment="昨收价")
    
    # 涨跌信息
    change_amount = Column(Float, nullable=False, comment="涨跌额")
    change_percent = Column(Float, nullable=False, comment="涨跌幅")
    
    # 成交信息
    volume = Column(Float, nullable=False, comment="成交量")
    amount = Column(Float, nullable=False, comment="成交额")
    turnover_rate = Column(Float, nullable=True, comment="换手率")
    
    # 买卖盘信息
    bid1_price = Column(Float, nullable=True, comment="买一价")
    bid1_volume = Column(Float, nullable=True, comment="买一量")
    ask1_price = Column(Float, nullable=True, comment="卖一价")
    ask1_volume = Column(Float, nullable=True, comment="卖一量")
    
    # 市值信息
    market_cap = Column(Float, nullable=True, comment="总市值")
    float_market_cap = Column(Float, nullable=True, comment="流通市值")
    
    # 时间字段
    quote_time = Column(DateTime, nullable=False, comment="行情时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    def __repr__(self):
        return f"<RealtimeQuotes(code='{self.code}', price={self.current_price}, change={self.change_percent}%)>"

class UserWatchlist(Base):
    """用户自选股模型"""
    __tablename__ = "user_watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False, comment="用户ID")
    stock_code = Column(String(20), index=True, nullable=False, comment="股票代码")
    
    # 自选股设置
    alert_price_high = Column(Float, nullable=True, comment="价格上限提醒")
    alert_price_low = Column(Float, nullable=True, comment="价格下限提醒")
    alert_change_percent = Column(Float, nullable=True, comment="涨跌幅提醒")
    
    # 备注信息
    notes = Column(Text, nullable=True, comment="备注")
    tags = Column(String(255), nullable=True, comment="标签")
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_user_stock', 'user_id', 'stock_code'),
    )
    
    def __repr__(self):
        return f"<UserWatchlist(user_id={self.user_id}, stock_code='{self.stock_code}')>"
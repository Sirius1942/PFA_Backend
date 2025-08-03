#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术指标数据模型
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base

class TechnicalIndicators(Base):
    """技术指标模型"""
    __tablename__ = "technical_indicators"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), index=True, nullable=False, comment="股票代码")
    date = Column(DateTime, index=True, nullable=False, comment="交易日期")
    
    # 移动平均线
    ma5 = Column(Float, nullable=True, comment="5日移动平均线")
    ma10 = Column(Float, nullable=True, comment="10日移动平均线")
    ma20 = Column(Float, nullable=True, comment="20日移动平均线")
    ma60 = Column(Float, nullable=True, comment="60日移动平均线")
    
    # MACD指标
    macd = Column(Float, nullable=True, comment="MACD线")
    macd_signal = Column(Float, nullable=True, comment="MACD信号线")
    macd_histogram = Column(Float, nullable=True, comment="MACD柱状图")
    
    # RSI指标
    rsi = Column(Float, nullable=True, comment="相对强弱指标")
    
    # KDJ指标
    kdj_k = Column(Float, nullable=True, comment="KDJ K值")
    kdj_d = Column(Float, nullable=True, comment="KDJ D值")
    kdj_j = Column(Float, nullable=True, comment="KDJ J值")
    
    # 布林带指标
    boll_upper = Column(Float, nullable=True, comment="布林带上轨")
    boll_middle = Column(Float, nullable=True, comment="布林带中轨")
    boll_lower = Column(Float, nullable=True, comment="布林带下轨")
    
    # 时间字段
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 创建复合索引和唯一约束
    __table_args__ = (
        Index('idx_code_date', 'code', 'date'),
        Index('idx_date_code', 'date', 'code'),
        UniqueConstraint('code', 'date', name='uq_technical_indicators_code_date'),
    )
    
    def __repr__(self):
        return f"<TechnicalIndicators(code='{self.code}', date='{self.date}', ma20={self.ma20})>"
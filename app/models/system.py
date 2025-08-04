#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统相关的数据库模型
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any

from app.core.database import Base


class SystemLog(Base):
    """系统日志模型"""
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), comment="日志时间")
    level = Column(String(20), nullable=False, comment="日志级别(INFO/WARNING/ERROR/DEBUG)")
    message = Column(Text, nullable=False, comment="日志消息")
    module = Column(String(50), nullable=False, comment="模块名称")
    user_id = Column(Integer, nullable=True, comment="关联用户ID")
    request_id = Column(String(100), nullable=True, comment="请求ID")
    ip_address = Column(String(45), nullable=True, comment="IP地址")
    user_agent = Column(String(500), nullable=True, comment="用户代理")
    extra_data = Column(JSON, nullable=True, comment="额外数据")
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.level}', module='{self.module}')>"


class SystemConfig(Base):
    """系统配置模型"""
    __tablename__ = "system_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键")
    value = Column(Text, nullable=False, comment="配置值")
    description = Column(String(500), nullable=True, comment="配置描述")
    category = Column(String(50), nullable=False, comment="配置分类")
    data_type = Column(String(20), default="string", comment="数据类型(string/int/float/bool/json)")
    is_public = Column(Boolean, default=False, comment="是否为公开配置")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(Integer, nullable=True, comment="更新者ID")
    
    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', category='{self.category}')>"


class SystemBackup(Base):
    """系统备份记录模型"""
    __tablename__ = "system_backups"
    
    id = Column(Integer, primary_key=True, index=True)
    backup_id = Column(String(100), unique=True, nullable=False, index=True, comment="备份ID")
    backup_type = Column(String(20), nullable=False, comment="备份类型(full/incremental/schema)")
    file_path = Column(String(500), nullable=False, comment="备份文件路径")
    file_size = Column(Integer, nullable=False, comment="文件大小(字节)")
    status = Column(String(20), default="running", comment="备份状态(running/completed/failed)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    completed_at = Column(DateTime(timezone=True), nullable=True, comment="完成时间")
    created_by = Column(Integer, nullable=False, comment="创建者ID")
    error_message = Column(Text, nullable=True, comment="错误信息")
    metadata = Column(JSON, nullable=True, comment="备份元数据")
    
    def __repr__(self):
        return f"<SystemBackup(backup_id='{self.backup_id}', status='{self.status}')>"


class PerformanceMetric(Base):
    """系统性能指标模型"""
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), comment="记录时间")
    cpu_usage = Column(Float, nullable=False, comment="CPU使用率(%)")
    memory_usage = Column(Float, nullable=False, comment="内存使用率(%)")
    disk_usage = Column(Float, nullable=False, comment="磁盘使用率(%)")
    network_io = Column(JSON, nullable=True, comment="网络IO统计")
    active_connections = Column(Integer, default=0, comment="活跃连接数")
    response_time = Column(Float, nullable=True, comment="平均响应时间(秒)")
    request_count = Column(Integer, default=0, comment="请求数量")
    error_count = Column(Integer, default=0, comment="错误数量")
    
    def __repr__(self):
        return f"<PerformanceMetric(timestamp={self.timestamp}, cpu={self.cpu_usage}%)>"


class MaintenanceMode(Base):
    """维护模式记录模型"""
    __tablename__ = "maintenance_mode"
    
    id = Column(Integer, primary_key=True, index=True)
    enabled = Column(Boolean, default=False, comment="是否启用维护模式")
    message = Column(Text, nullable=True, comment="维护提示信息")
    start_time = Column(DateTime(timezone=True), nullable=True, comment="维护开始时间")
    end_time = Column(DateTime(timezone=True), nullable=True, comment="维护结束时间")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    updated_by = Column(Integer, nullable=False, comment="操作者ID")
    
    def __repr__(self):
        return f"<MaintenanceMode(enabled={self.enabled})>"
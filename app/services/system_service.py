#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统服务
"""

import logging
import os
import psutil
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_

from app.models.system import (
    SystemLog, SystemConfig, SystemBackup, 
    PerformanceMetric, MaintenanceMode
)

logger = logging.getLogger(__name__)


class SystemService:
    """系统服务类"""
    
    def create_log_entry(
        self,
        db: Session,
        level: str,
        message: str,
        module: str,
        user_id: Optional[int] = None,
        request_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> SystemLog:
        """创建系统日志条目"""
        log_entry = SystemLog(
            level=level.upper(),
            message=message,
            module=module,
            user_id=user_id,
            request_id=request_id,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    
    def get_system_logs(
        self,
        db: Session,
        level: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        module: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """获取系统日志"""
        query = db.query(SystemLog)
        
        # 应用过滤条件
        if level:
            query = query.filter(SystemLog.level == level.upper())
        if start_time:
            query = query.filter(SystemLog.timestamp >= start_time)
        if end_time:
            query = query.filter(SystemLog.timestamp <= end_time)
        if module:
            query = query.filter(SystemLog.module == module)
        if user_id:
            query = query.filter(SystemLog.user_id == user_id)
        
        # 获取总数
        total = query.count()
        
        # 分页和排序
        logs = query.order_by(desc(SystemLog.timestamp)).offset(offset).limit(limit).all()
        
        return {
            "logs": [
                {
                    "id": log.id,
                    "timestamp": log.timestamp,
                    "level": log.level,
                    "message": log.message,
                    "module": log.module,
                    "user_id": log.user_id,
                    "request_id": log.request_id,
                    "ip_address": log.ip_address,
                    "extra_data": log.extra_data
                } for log in logs
            ],
            "total": total,
            "filters": {
                "level": level,
                "start_time": start_time,
                "end_time": end_time,
                "module": module,
                "user_id": user_id
            }
        }
    
    def get_current_performance(self) -> Dict[str, Any]:
        """获取当前性能指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 网络IO
            network = psutil.net_io_counters()
            
            # 活跃连接数
            active_connections = len(psutil.net_connections())
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": (disk.used / disk.total) * 100,
                "network_io": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                },
                "active_connections": active_connections,
                "response_time": None,  # 这个需要从其他地方获取
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"获取性能指标失败: {str(e)}")
            return {}


# 创建服务实例
system_service = SystemService()
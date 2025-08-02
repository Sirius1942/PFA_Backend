from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import os
import psutil
import json

from app.core.database import get_db, check_db_connection
from app.models.user import User
from app.core.deps import get_current_user
from app.auth.permissions import require_permission, Permissions, require_admin
from pydantic import BaseModel

router = APIRouter(prefix="/system", tags=["系统管理"])

# Pydantic模型
class SystemStatus(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, Any]
    performance: Dict[str, Any]

class LogEntry(BaseModel):
    timestamp: datetime
    level: str
    message: str
    module: Optional[str] = None
    user_id: Optional[int] = None

class SystemConfig(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None
    category: Optional[str] = None

class SystemConfigUpdate(BaseModel):
    value: Any
    description: Optional[str] = None

class DatabaseStats(BaseModel):
    total_users: int
    active_users: int
    total_stocks: int
    total_watchlist_items: int
    database_size: Optional[str] = None
    last_backup: Optional[datetime] = None

class PerformanceMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, int]
    active_connections: int
    response_time: float

@router.get("/health")
async def health_check():
    """系统健康检查（公开接口）"""
    try:
        # 检查数据库连接
        db_status = await check_db_connection()
        
        return {
            "status": "healthy" if db_status else "unhealthy",
            "timestamp": datetime.utcnow(),
            "services": {
                "database": "up" if db_status else "down",
                "api": "up"
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow(),
            "error": str(e)
        }

@router.get("/status", response_model=SystemStatus)
@require_admin()
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取系统状态（管理员权限）"""
    try:
        # 检查各服务状态
        db_status = await check_db_connection()
        
        # 获取系统性能指标
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 网络IO统计
        network = psutil.net_io_counters()
        
        return SystemStatus(
            status="healthy",
            timestamp=datetime.utcnow(),
            services={
                "database": "up" if db_status else "down",
                "redis": "up",  # 实际应该检查Redis连接
                "api": "up"
            },
            performance={
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "disk_usage": (disk.used / disk.total) * 100,
                "network_io": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统状态失败: {str(e)}"
        )

@router.get("/performance", response_model=PerformanceMetrics)
@require_admin()
async def get_performance_metrics(
    current_user: User = Depends(get_current_user)
):
    """获取性能指标（管理员权限）"""
    try:
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # 内存使用情况
        memory = psutil.virtual_memory()
        
        # 磁盘使用情况
        disk = psutil.disk_usage('/')
        
        # 网络IO
        network = psutil.net_io_counters()
        
        # 活跃连接数（模拟）
        active_connections = len(psutil.net_connections())
        
        return PerformanceMetrics(
            cpu_usage=cpu_percent,
            memory_usage=memory.percent,
            disk_usage=(disk.used / disk.total) * 100,
            network_io={
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            },
            active_connections=active_connections,
            response_time=0.05  # 模拟响应时间
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取性能指标失败: {str(e)}"
        )

@router.get("/database/stats", response_model=DatabaseStats)
@require_admin()
async def get_database_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取数据库统计信息（管理员权限）"""
    try:
        from app.models.user import User
        from app.models.stock import StockInfo, UserWatchlist
        
        # 统计用户数据
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # 统计股票数据
        total_stocks = db.query(StockInfo).filter(StockInfo.is_active == True).count()
        
        # 统计自选股数据
        total_watchlist_items = db.query(UserWatchlist).count()
        
        return DatabaseStats(
            total_users=total_users,
            active_users=active_users,
            total_stocks=total_stocks,
            total_watchlist_items=total_watchlist_items,
            database_size="未知",  # 需要具体的数据库查询
            last_backup=None  # 需要备份系统集成
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取数据库统计失败: {str(e)}"
        )

@router.get("/logs")
@require_permission(Permissions.VIEW_LOGS)
async def get_system_logs(
    level: Optional[str] = Query(None, description="日志级别过滤"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """获取系统日志（需要查看日志权限）"""
    try:
        # 这里应该从实际的日志系统读取日志
        # 现在返回模拟数据
        logs = []
        
        # 模拟日志条目
        log_levels = ["INFO", "WARNING", "ERROR", "DEBUG"]
        modules = ["auth", "api", "database", "system"]
        
        for i in range(min(limit, 50)):
            log_entry = {
                "timestamp": datetime.utcnow() - timedelta(minutes=i*5),
                "level": log_levels[i % len(log_levels)],
                "message": f"模拟日志消息 {i+1}",
                "module": modules[i % len(modules)],
                "user_id": current_user.id if i % 3 == 0 else None
            }
            
            # 应用过滤器
            if level and log_entry["level"] != level.upper():
                continue
            
            if start_time and log_entry["timestamp"] < start_time:
                continue
                
            if end_time and log_entry["timestamp"] > end_time:
                continue
            
            logs.append(log_entry)
        
        return {
            "logs": logs,
            "total": len(logs),
            "filters": {
                "level": level,
                "start_time": start_time,
                "end_time": end_time
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取系统日志失败: {str(e)}"
        )

@router.get("/config")
@require_permission(Permissions.MANAGE_SETTINGS)
async def get_system_config(
    category: Optional[str] = Query(None, description="配置分类"),
    current_user: User = Depends(get_current_user)
):
    """获取系统配置（需要管理设置权限）"""
    # 模拟系统配置
    configs = [
        {
            "key": "app.name",
            "value": "私人金融分析师",
            "description": "应用名称",
            "category": "app"
        },
        {
            "key": "app.version",
            "value": "1.0.0",
            "description": "应用版本",
            "category": "app"
        },
        {
            "key": "security.jwt_expire_minutes",
            "value": 30,
            "description": "JWT令牌过期时间（分钟）",
            "category": "security"
        },
        {
            "key": "api.rate_limit",
            "value": 1000,
            "description": "API速率限制（每小时）",
            "category": "api"
        },
        {
            "key": "data.cache_expire_seconds",
            "value": 300,
            "description": "数据缓存过期时间（秒）",
            "category": "data"
        }
    ]
    
    if category:
        configs = [c for c in configs if c["category"] == category]
    
    return {
        "configs": configs,
        "categories": list(set(c["category"] for c in configs))
    }

@router.put("/config/{config_key}")
@require_permission(Permissions.MANAGE_SETTINGS)
async def update_system_config(
    config_key: str,
    config_update: SystemConfigUpdate,
    current_user: User = Depends(get_current_user)
):
    """更新系统配置（需要管理设置权限）"""
    # 这里应该更新实际的配置存储
    # 现在返回模拟响应
    
    return {
        "message": f"配置 {config_key} 更新成功",
        "key": config_key,
        "old_value": "旧值",
        "new_value": config_update.value,
        "updated_by": current_user.username,
        "updated_at": datetime.utcnow()
    }

@router.post("/backup")
@require_admin()
async def create_backup(
    backup_type: str = Query("full", description="备份类型：full/incremental"),
    current_user: User = Depends(get_current_user)
):
    """创建系统备份（管理员权限）"""
    try:
        # 这里应该实现实际的备份逻辑
        backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        return {
            "message": "备份任务已启动",
            "backup_id": backup_id,
            "backup_type": backup_type,
            "started_by": current_user.username,
            "started_at": datetime.utcnow(),
            "estimated_completion": datetime.utcnow() + timedelta(minutes=30)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建备份失败: {str(e)}"
        )

@router.get("/backup/list")
@require_admin()
async def list_backups(
    current_user: User = Depends(get_current_user)
):
    """获取备份列表（管理员权限）"""
    # 模拟备份列表
    backups = [
        {
            "id": "backup_20241201_120000",
            "type": "full",
            "size": "1.2GB",
            "created_at": datetime.utcnow() - timedelta(days=1),
            "status": "completed"
        },
        {
            "id": "backup_20241130_120000",
            "type": "incremental",
            "size": "256MB",
            "created_at": datetime.utcnow() - timedelta(days=2),
            "status": "completed"
        }
    ]
    
    return {
        "backups": backups,
        "total": len(backups)
    }

@router.post("/maintenance")
@require_admin()
async def toggle_maintenance_mode(
    enabled: bool = Query(..., description="是否启用维护模式"),
    message: Optional[str] = Query(None, description="维护提示信息"),
    current_user: User = Depends(get_current_user)
):
    """切换维护模式（管理员权限）"""
    # 这里应该实现实际的维护模式切换逻辑
    
    return {
        "message": f"维护模式已{'启用' if enabled else '禁用'}",
        "maintenance_enabled": enabled,
        "maintenance_message": message or "系统正在维护中，请稍后再试",
        "updated_by": current_user.username,
        "updated_at": datetime.utcnow()
    }

@router.get("/info")
async def get_system_info():
    """获取系统基本信息（公开接口）"""
    return {
        "app_name": "私人金融分析师",
        "version": "1.0.0",
        "api_version": "v1",
        "build_time": "2024-12-01T12:00:00Z",
        "environment": "development",
        "features": [
            "用户认证",
            "股票数据",
            "AI助手",
            "实时行情",
            "自选股管理"
        ]
    }
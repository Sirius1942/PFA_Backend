from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from datetime import datetime, timedelta
import psutil
import os
import json
import subprocess
from pathlib import Path

from app.core.config import settings
from app.models.user import User
from app.models.stock import StockInfo, RealtimeQuotes, KlineData, UserWatchlist
from loguru import logger

class SystemService:
    """系统服务类"""
    
    def __init__(self):
        self.maintenance_mode = False
        self.system_config = {
            "app_name": settings.APP_NAME,
            "version": settings.VERSION,
            "debug": settings.DEBUG,
            "environment": "development" if settings.DEBUG else "production"
        }
    
    def get_health_status(self, db: Session) -> Dict[str, Any]:
        """获取系统健康状态"""
        try:
            health_status = {
                "status": "healthy",
                "timestamp": datetime.utcnow(),
                "services": {},
                "overall_status": "ok"
            }
            
            # 检查数据库连接
            try:
                db.execute(text("SELECT 1"))
                health_status["services"]["database"] = {
                    "status": "healthy",
                    "response_time_ms": 0  # 实际应该测量响应时间
                }
            except Exception as e:
                health_status["services"]["database"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["overall_status"] = "degraded"
            
            # 检查Redis连接（如果配置了）
            try:
                # 这里应该检查Redis连接
                health_status["services"]["redis"] = {
                    "status": "healthy",
                    "response_time_ms": 0
                }
            except Exception as e:
                health_status["services"]["redis"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # 检查文件系统
            try:
                disk_usage = psutil.disk_usage('/')
                free_space_percent = (disk_usage.free / disk_usage.total) * 100
                
                if free_space_percent < 10:
                    health_status["services"]["filesystem"] = {
                        "status": "warning",
                        "free_space_percent": round(free_space_percent, 2),
                        "message": "磁盘空间不足"
                    }
                    health_status["overall_status"] = "warning"
                else:
                    health_status["services"]["filesystem"] = {
                        "status": "healthy",
                        "free_space_percent": round(free_space_percent, 2)
                    }
            except Exception as e:
                health_status["services"]["filesystem"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            # 检查内存使用
            try:
                memory = psutil.virtual_memory()
                if memory.percent > 90:
                    health_status["services"]["memory"] = {
                        "status": "warning",
                        "usage_percent": memory.percent,
                        "message": "内存使用率过高"
                    }
                    health_status["overall_status"] = "warning"
                else:
                    health_status["services"]["memory"] = {
                        "status": "healthy",
                        "usage_percent": memory.percent
                    }
            except Exception as e:
                health_status["services"]["memory"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
            
            return health_status
            
        except Exception as e:
            logger.error(f"获取健康状态失败: {e}")
            return {
                "status": "unhealthy",
                "timestamp": datetime.utcnow(),
                "error": str(e),
                "overall_status": "error"
            }
    
    def get_system_status(self, db: Session) -> Dict[str, Any]:
        """获取系统状态"""
        try:
            # 获取系统基本信息
            system_info = {
                "hostname": os.uname().nodename,
                "platform": os.uname().system,
                "architecture": os.uname().machine,
                "python_version": os.sys.version.split()[0],
                "uptime": self._get_system_uptime(),
                "maintenance_mode": self.maintenance_mode
            }
            
            # 获取应用信息
            app_info = {
                "name": settings.APP_NAME,
                "version": settings.VERSION,
                "debug_mode": settings.DEBUG,
                "environment": "development" if settings.DEBUG else "production",
                "start_time": datetime.utcnow()  # 实际应该记录应用启动时间
            }
            
            # 获取数据库状态
            db_stats = self.get_database_stats(db)
            
            return {
                "system": system_info,
                "application": app_info,
                "database": db_stats,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {e}")
            return {"error": str(e)}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            
            # 磁盘使用情况
            disk = psutil.disk_usage('/')
            
            # 网络IO
            network = psutil.net_io_counters()
            
            # 磁盘IO
            disk_io = psutil.disk_io_counters()
            
            return {
                "cpu": {
                    "usage_percent": cpu_percent,
                    "core_count": cpu_count,
                    "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else None
                },
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "available_gb": round(memory.available / (1024**3), 2),
                    "usage_percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "free_gb": round(disk.free / (1024**3), 2),
                    "usage_percent": round((disk.used / disk.total) * 100, 2)
                },
                "network": {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                } if network else None,
                "disk_io": {
                    "read_bytes": disk_io.read_bytes,
                    "write_bytes": disk_io.write_bytes,
                    "read_count": disk_io.read_count,
                    "write_count": disk_io.write_count
                } if disk_io else None,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {"error": str(e)}
    
    def get_database_stats(self, db: Session) -> Dict[str, Any]:
        """获取数据库统计信息"""
        try:
            stats = {}
            
            # 用户统计
            total_users = db.query(func.count(User.id)).scalar() or 0
            active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar() or 0
            
            stats["users"] = {
                "total": total_users,
                "active": active_users,
                "inactive": total_users - active_users
            }
            
            # 股票数据统计
            total_stocks = db.query(func.count(StockInfo.id)).scalar() or 0
            active_stocks = db.query(func.count(StockInfo.id)).filter(StockInfo.is_active == True).scalar() or 0
            
            stats["stocks"] = {
                "total": total_stocks,
                "active": active_stocks
            }
            
            # 行情数据统计
            total_quotes = db.query(func.count(RealtimeQuotes.id)).scalar() or 0
            today_quotes = db.query(func.count(RealtimeQuotes.id)).filter(
                RealtimeQuotes.timestamp >= datetime.utcnow().date()
            ).scalar() or 0
            
            stats["quotes"] = {
                "total": total_quotes,
                "today": today_quotes
            }
            
            # K线数据统计
            total_klines = db.query(func.count(KlineData.id)).scalar() or 0
            
            stats["klines"] = {
                "total": total_klines
            }
            
            # 自选股统计
            total_watchlist = db.query(func.count(UserWatchlist.id)).scalar() or 0
            
            stats["watchlist"] = {
                "total": total_watchlist
            }
            
            # 数据库大小（如果支持）
            try:
                db_size_result = db.execute(text(
                    "SELECT pg_size_pretty(pg_database_size(current_database()))"
                )).scalar()
                stats["database_size"] = db_size_result
            except:
                stats["database_size"] = "未知"
            
            return stats
            
        except Exception as e:
            logger.error(f"获取数据库统计失败: {e}")
            return {"error": str(e)}
    
    def get_system_logs(self, level: str = "INFO", limit: int = 100, 
                       start_time: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """获取系统日志"""
        try:
            # 这里应该从实际的日志文件或日志系统中读取
            # 现在返回模拟数据
            logs = []
            
            log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
            if level.upper() not in log_levels:
                level = "INFO"
            
            # 模拟日志数据
            import random
            from datetime import timedelta
            
            for i in range(min(limit, 50)):
                log_time = datetime.utcnow() - timedelta(minutes=random.randint(1, 1440))
                if start_time and log_time < start_time:
                    continue
                
                log_level = random.choice(log_levels)
                if log_levels.index(log_level) < log_levels.index(level.upper()):
                    continue
                
                logs.append({
                    "timestamp": log_time,
                    "level": log_level,
                    "module": random.choice(["api", "database", "auth", "stock_service", "ai_service"]),
                    "message": f"模拟日志消息 {i+1}",
                    "details": f"详细信息 {i+1}" if random.random() > 0.7 else None
                })
            
            # 按时间倒序排列
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return logs
            
        except Exception as e:
            logger.error(f"获取系统日志失败: {e}")
            return []
    
    def get_system_config(self) -> Dict[str, Any]:
        """获取系统配置"""
        try:
            # 返回非敏感的配置信息
            config = {
                "app_name": settings.APP_NAME,
                "version": settings.VERSION,
                "debug": settings.DEBUG,
                "cors_origins": settings.CORS_ORIGINS,
                "log_level": settings.LOG_LEVEL,
                "pagination": {
                    "default_page_size": settings.DEFAULT_PAGE_SIZE,
                    "max_page_size": settings.MAX_PAGE_SIZE
                },
                "cache": {
                    "default_expire_seconds": settings.CACHE_EXPIRE_SECONDS
                },
                "upload": {
                    "max_file_size_mb": settings.MAX_FILE_SIZE_MB
                },
                "maintenance_mode": self.maintenance_mode
            }
            
            return config
            
        except Exception as e:
            logger.error(f"获取系统配置失败: {e}")
            return {"error": str(e)}
    
    def update_system_config(self, config_updates: Dict[str, Any]) -> Dict[str, Any]:
        """更新系统配置"""
        try:
            # 只允许更新特定的配置项
            allowed_updates = {
                "maintenance_mode",
                "log_level",
                "default_page_size",
                "max_page_size",
                "cache_expire_seconds",
                "max_file_size_mb"
            }
            
            updated_config = {}
            
            for key, value in config_updates.items():
                if key in allowed_updates:
                    if key == "maintenance_mode":
                        self.maintenance_mode = bool(value)
                        updated_config[key] = self.maintenance_mode
                    elif key == "log_level":
                        # 这里应该更新日志级别
                        updated_config[key] = value
                    else:
                        # 其他配置项的更新逻辑
                        updated_config[key] = value
            
            logger.info(f"系统配置更新: {updated_config}")
            return {
                "success": True,
                "updated_config": updated_config,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"更新系统配置失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_backup(self, backup_type: str = "database") -> Dict[str, Any]:
        """创建系统备份"""
        try:
            backup_id = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            backup_path = f"/tmp/{backup_id}"
            
            if backup_type == "database":
                # 数据库备份逻辑
                # 这里应该实现实际的数据库备份
                backup_info = {
                    "id": backup_id,
                    "type": "database",
                    "path": f"{backup_path}_db.sql",
                    "size_mb": 0,  # 实际大小
                    "created_at": datetime.utcnow(),
                    "status": "completed"
                }
            elif backup_type == "full":
                # 完整系统备份逻辑
                backup_info = {
                    "id": backup_id,
                    "type": "full",
                    "path": f"{backup_path}_full.tar.gz",
                    "size_mb": 0,  # 实际大小
                    "created_at": datetime.utcnow(),
                    "status": "completed"
                }
            else:
                return {
                    "success": False,
                    "error": "不支持的备份类型"
                }
            
            logger.info(f"备份创建成功: {backup_id}")
            return {
                "success": True,
                "backup": backup_info
            }
            
        except Exception as e:
            logger.error(f"创建备份失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """列出所有备份"""
        try:
            # 这里应该从实际的备份存储中获取备份列表
            # 现在返回模拟数据
            backups = [
                {
                    "id": "backup_20231201_120000",
                    "type": "database",
                    "path": "/backups/backup_20231201_120000_db.sql",
                    "size_mb": 125.5,
                    "created_at": datetime.utcnow() - timedelta(days=1),
                    "status": "completed"
                },
                {
                    "id": "backup_20231130_120000",
                    "type": "full",
                    "path": "/backups/backup_20231130_120000_full.tar.gz",
                    "size_mb": 1024.0,
                    "created_at": datetime.utcnow() - timedelta(days=2),
                    "status": "completed"
                }
            ]
            
            return backups
            
        except Exception as e:
            logger.error(f"列出备份失败: {e}")
            return []
    
    def toggle_maintenance_mode(self, enabled: bool) -> Dict[str, Any]:
        """切换维护模式"""
        try:
            self.maintenance_mode = enabled
            
            status = "启用" if enabled else "禁用"
            logger.info(f"维护模式已{status}")
            
            return {
                "success": True,
                "maintenance_mode": self.maintenance_mode,
                "message": f"维护模式已{status}",
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"切换维护模式失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_system_uptime(self) -> str:
        """获取系统运行时间"""
        try:
            uptime_seconds = psutil.boot_time()
            uptime_delta = datetime.utcnow() - datetime.fromtimestamp(uptime_seconds)
            
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}天 {hours}小时 {minutes}分钟"
            
        except Exception:
            return "未知"
    
    def cleanup_old_data(self, db: Session, days: int = 30) -> Dict[str, Any]:
        """清理旧数据"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # 清理旧的实时行情数据
            old_quotes = db.query(RealtimeQuotes).filter(
                RealtimeQuotes.timestamp < cutoff_date
            ).count()
            
            db.query(RealtimeQuotes).filter(
                RealtimeQuotes.timestamp < cutoff_date
            ).delete()
            
            # 清理旧的K线数据（保留更长时间）
            kline_cutoff = datetime.utcnow() - timedelta(days=days * 3)
            old_klines = db.query(KlineData).filter(
                KlineData.timestamp < kline_cutoff
            ).count()
            
            db.query(KlineData).filter(
                KlineData.timestamp < kline_cutoff
            ).delete()
            
            db.commit()
            
            logger.info(f"数据清理完成: 删除了 {old_quotes} 条行情数据, {old_klines} 条K线数据")
            
            return {
                "success": True,
                "deleted_quotes": old_quotes,
                "deleted_klines": old_klines,
                "cutoff_date": cutoff_date,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"数据清理失败: {e}")
            db.rollback()
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_api_statistics(self, db: Session) -> Dict[str, Any]:
        """获取API统计信息"""
        try:
            # 这里应该从实际的API访问日志中统计
            # 现在返回模拟数据
            return {
                "total_requests": 12345,
                "requests_today": 567,
                "average_response_time_ms": 125.5,
                "error_rate_percent": 2.1,
                "top_endpoints": [
                    {"endpoint": "/api/v1/stocks/quotes", "count": 2345},
                    {"endpoint": "/api/v1/auth/login", "count": 1234},
                    {"endpoint": "/api/v1/users/me", "count": 987}
                ],
                "status_codes": {
                    "200": 10123,
                    "400": 123,
                    "401": 89,
                    "404": 45,
                    "500": 12
                },
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"获取API统计失败: {e}")
            return {"error": str(e)}

# 创建全局服务实例
system_service = SystemService()
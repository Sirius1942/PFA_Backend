from functools import wraps
from typing import List, Union
from fastapi import HTTPException, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.core.deps import get_current_user

def require_permission(permission: Union[str, List[str]]):
    """
    权限装饰器，用于检查用户是否具有指定权限
    
    Args:
        permission: 权限名称或权限名称列表
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未找到用户信息"
                )
            
            # 检查权限
            if isinstance(permission, str):
                required_permissions = [permission]
            else:
                required_permissions = permission
            
            if not current_user.has_permissions(required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="权限不足"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_role(role: Union[str, List[str]]):
    """
    角色装饰器，用于检查用户是否具有指定角色
    
    Args:
        role: 角色名称或角色名称列表
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 从kwargs中获取current_user
            current_user = None
            for key, value in kwargs.items():
                if isinstance(value, User):
                    current_user = value
                    break
            
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未找到用户信息"
                )
            
            # 检查角色
            if isinstance(role, str):
                required_roles = [role]
            else:
                required_roles = role
            
            user_roles = [r.name for r in current_user.roles]
            if not any(r in user_roles for r in required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="角色权限不足"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator

def require_admin():
    """
    管理员装饰器，要求用户具有管理员角色
    """
    return require_role("admin")

def check_user_permission(user: User, permission: str) -> bool:
    """
    检查用户是否具有指定权限
    
    Args:
        user: 用户对象
        permission: 权限名称
    
    Returns:
        bool: 是否具有权限
    """
    return user.has_permissions([permission])

def check_user_role(user: User, role: str) -> bool:
    """
    检查用户是否具有指定角色
    
    Args:
        user: 用户对象
        role: 角色名称
    
    Returns:
        bool: 是否具有角色
    """
    user_roles = [r.name for r in user.roles]
    return role in user_roles

def get_user_permissions(user: User) -> List[str]:
    """
    获取用户的所有权限
    
    Args:
        user: 用户对象
    
    Returns:
        List[str]: 权限名称列表
    """
    permissions = set()
    for role in user.roles:
        for permission in role.permissions:
            permissions.add(permission.name)
    return list(permissions)

def get_user_roles(user: User) -> List[str]:
    """
    获取用户的所有角色
    
    Args:
        user: 用户对象
    
    Returns:
        List[str]: 角色名称列表
    """
    return [role.name for role in user.roles]

# 权限常量定义
class Permissions:
    """权限常量类"""
    
    # 用户管理权限
    MANAGE_USERS = "user.create"  # 更新为匹配数据库
    VIEW_USERS = "user.view"      # 更新为匹配数据库
    
    # 股票数据权限
    VIEW_STOCKS = "stock.view"       # 更新为匹配数据库
    MANAGE_STOCKS = "stock.manage"   # 保持一致的命名规则
    VIEW_REALTIME_DATA = "stock.realtime"  # 更新为匹配数据库
    
    # 自选股权限
    MANAGE_WATCHLIST = "stock.watchlist"  # 更新为匹配数据库
    
    # AI助手权限
    USE_AI_ASSISTANT = "agent.chat"     # 更新为匹配数据库
    MANAGE_AI_SETTINGS = "agent.analysis"  # 更新为匹配数据库
    
    # 系统管理权限
    SYSTEM_ADMIN = "admin.system"    # 更新为匹配数据库
    VIEW_LOGS = "admin.logs"         # 保持一致的命名规则
    MANAGE_SETTINGS = "admin.settings"  # 保持一致的命名规则
    
    # 数据分析权限
    ADVANCED_ANALYSIS = "data.analysis"  # 保持一致的命名规则
    EXPORT_DATA = "data.export"          # 保持一致的命名规则

class Roles:
    """角色常量类"""
    
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"
    VIEWER = "viewer"
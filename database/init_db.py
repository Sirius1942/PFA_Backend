#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
创建默认用户、角色和权限
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User, Role, Permission, user_roles, role_permissions
from app.auth.jwt import PasswordManager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_default_permissions(db: Session):
    """创建默认权限"""
    permissions = [
        {"code": "manage_users", "name": "用户管理", "description": "管理用户账户", "module": "user"},
        {"code": "view_users", "name": "查看用户", "description": "查看用户信息", "module": "user"},
        {"code": "manage_stocks", "name": "股票管理", "description": "管理股票数据", "module": "stock"},
        {"code": "view_stocks", "name": "查看股票", "description": "查看股票信息", "module": "stock"},
        {"code": "use_ai_assistant", "name": "AI助手", "description": "使用AI助手功能", "module": "ai"},
        {"code": "manage_system", "name": "系统管理", "description": "系统配置管理", "module": "system"},
    ]
    
    for perm_data in permissions:
        existing = db.query(Permission).filter(Permission.code == perm_data["code"]).first()
        if not existing:
            permission = Permission(**perm_data)
            db.add(permission)
            logger.info(f"创建权限: {perm_data['name']}")
    
    db.commit()

def create_default_roles(db: Session):
    """创建默认角色"""
    roles = [
        {
            "name": "admin",
            "display_name": "管理员",
            "description": "系统管理员，拥有所有权限",
            "permissions": ["manage_users", "view_users", "manage_stocks", "view_stocks", "use_ai_assistant", "manage_system"]
        },
        {
            "name": "user",
            "display_name": "普通用户",
            "description": "普通用户，基础功能权限",
            "permissions": ["view_stocks", "use_ai_assistant"]
        }
    ]
    
    for role_data in roles:
        existing = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not existing:
            role = Role(
                name=role_data["name"],
                display_name=role_data["display_name"],
                description=role_data["description"]
            )
            
            # 分配权限
            permissions = db.query(Permission).filter(Permission.code.in_(role_data["permissions"])).all()
            role.permissions = permissions
            
            db.add(role)
            logger.info(f"创建角色: {role_data['display_name']}")
    
    db.commit()

def create_default_users(db: Session):
    """创建默认用户"""
    password_manager = PasswordManager()
    
    users = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "password": "admin123",
            "full_name": "系统管理员",
            "is_superuser": True,
            "roles": ["admin"]
        },
        {
            "username": "test",
            "email": "test@example.com",
            "password": "test123",
            "full_name": "测试用户",
            "is_superuser": False,
            "roles": ["user"]
        }
    ]
    
    for user_data in users:
        existing = db.query(User).filter(User.username == user_data["username"]).first()
        if not existing:
            user = User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=password_manager.hash_password(user_data["password"]),
                full_name=user_data["full_name"],
                is_active=True,
                is_superuser=user_data["is_superuser"]
            )
            
            # 分配角色
            roles = db.query(Role).filter(Role.name.in_(user_data["roles"])).all()
            user.roles = roles
            
            db.add(user)
            logger.info(f"创建用户: {user_data['username']} (密码: {user_data['password']})")
    
    db.commit()

def init_database():
    """初始化数据库"""
    try:
        # 创建所有表
        Base.metadata.create_all(bind=engine)
        logger.info("数据库表创建成功")
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 创建默认数据
            create_default_permissions(db)
            create_default_roles(db)
            create_default_users(db)
            
            logger.info("数据库初始化完成！")
            logger.info("默认管理员账户: admin / admin123")
            logger.info("默认测试账户: test / test123")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        raise

if __name__ == "__main__":
    init_database()
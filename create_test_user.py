#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户脚本
"""

import sys
import asyncio
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.services.user_service import user_service
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_test_users():
    """创建测试用户"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # 检查是否已存在admin用户
        existing_admin = db.query(User).filter(User.username == "admin").first()
        if existing_admin:
            print("✅ admin用户已存在")
        else:
            # 创建admin用户
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=pwd_context.hash("admin123"),
                full_name="系统管理员",
                is_active=True,
                is_superuser=True
            )
            db.add(admin_user)
            print("✅ 创建admin用户成功")
        
        # 检查是否已存在test用户
        existing_test = db.query(User).filter(User.username == "test").first()
        if existing_test:
            print("✅ test用户已存在")
        else:
            # 创建test用户
            test_user = User(
                username="test",
                email="test@example.com",
                hashed_password=pwd_context.hash("test123"),
                full_name="测试用户",
                is_active=True,
                is_superuser=False
            )
            db.add(test_user)
            print("✅ 创建test用户成功")
        
        db.commit()
        
        print("\n🎉 用户创建完成！")
        print("\n📋 测试账号信息:")
        print("  管理员账号:")
        print("    用户名: admin")
        print("    密码: admin123")
        print("  普通用户账号:")
        print("    用户名: test")
        print("    密码: test123")
        
    except Exception as e:
        print(f"❌ 创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()

def list_users():
    """列出所有用户"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print("\n👥 当前用户列表:")
        print("-" * 60)
        for user in users:
            status = "✅ 活跃" if user.is_active else "❌ 禁用"
            role = "🔑 管理员" if user.is_superuser else "👤 普通用户"
            print(f"  {user.username:<10} | {user.email:<20} | {role} | {status}")
        print("-" * 60)
        print(f"总计: {len(users)} 个用户")
    except Exception as e:
        print(f"❌ 查询用户失败: {e}")
    finally:
        db.close()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "list":
        list_users()
    else:
        create_test_users()
        list_users()

if __name__ == "__main__":
    main()
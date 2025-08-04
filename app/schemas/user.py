#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户相关的Pydantic模型
"""

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    hashed_password: str
    is_verified: bool = False
    is_superuser: bool = False
    login_count: int = 0
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserResponse(UserBase):
    """用户响应模型"""
    id: int
    is_verified: bool
    is_superuser: bool
    login_count: int
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: List[str] = []  # 添加roles字段
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    users: List[UserResponse]
    total: int
    page: int
    size: int


class PasswordChange(BaseModel):
    """密码修改模型"""
    old_password: str
    new_password: str


class UserStats(BaseModel):
    """用户统计模型"""
    total_watchlist: int
    total_portfolios: int
    total_analyses: int
    last_login: Optional[datetime] = None
    member_since: datetime
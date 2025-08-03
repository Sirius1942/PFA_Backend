#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关的数据模型
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    is_active: bool = True


class UserCreate(UserBase):
    """用户创建模型"""
    password: str


class UserRegister(BaseModel):
    """用户注册模型"""
    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    hashed_password: str

    class Config:
        from_attributes = True


class User(UserBase):
    """用户响应模型"""
    id: int

    class Config:
        from_attributes = True


class UserProfile(UserBase):
    """用户资料模型"""
    id: int
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    is_verified: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    roles: List[str] = []
    permissions: List[str] = []
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """令牌模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据模型"""
    username: Optional[str] = None


class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str


class PasswordReset(BaseModel):
    """密码重置模型"""
    token: str
    new_password: str


class PasswordResetRequest(BaseModel):
    """密码重置请求模型"""
    email: EmailStr
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证相关API
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.models.user import User, Role
from app.auth.jwt import jwt_manager, password_manager
from app.schemas.auth import (
    UserRegister, UserLogin, Token, UserProfile,
    PasswordReset, PasswordResetRequest
)
from app.services.user_service import user_service
from app.core.deps import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

@router.post("/register", response_model=Dict[str, Any], summary="用户注册")
async def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """用户注册"""
    try:
        # 检查用户名是否已存在
        if user_service.get_user_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        if user_service.get_user_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建用户
        user = user_service.create_user(db, user_data)
        
        # 分配默认角色
        default_role = user_service.get_role_by_name(db, "user")
        if default_role:
            user_service.assign_role_to_user(db, user.id, default_role.id)
        
        logger.info(f"用户注册成功: {user.username}")
        
        return {
            "message": "注册成功",
            "user_id": user.id,
            "username": user.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户注册失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="注册失败，请稍后重试"
        )

@router.post("/login", response_model=Token, summary="用户登录")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """用户登录"""
    try:
        # 验证用户
        user = user_service.authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户名或密码错误",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # 检查用户状态
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="账户已被禁用"
            )
        
        # 创建令牌
        access_token = jwt_manager.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        refresh_token = jwt_manager.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        logger.info(f"用户登录成功: {user.username}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": jwt_manager.access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"用户登录失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="登录失败，请稍后重试"
        )

@router.post("/refresh", response_model=Token, summary="刷新令牌")
async def refresh_token(
    refresh_token: str = Form(...),
    db: Session = Depends(get_db)
):
    """刷新访问令牌"""
    try:
        # 验证刷新令牌
        payload = jwt_manager.verify_token(refresh_token, "refresh")
        user_id = int(payload.get("sub"))
        
        user = user_service.get_user_by_id(db, user_id)
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="用户不存在或已被禁用"
            )
        
        # 创建新的访问令牌
        access_token = jwt_manager.create_access_token(
            data={"sub": str(user.id), "username": user.username}
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": jwt_manager.access_token_expire_minutes * 60
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"令牌刷新失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌刷新失败"
        )

@router.get("/profile", response_model=UserProfile, summary="获取用户信息")
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        avatar=current_user.avatar,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login,
        roles=[role.name for role in current_user.roles],
        permissions=current_user.permissions
    )

@router.post("/logout", summary="用户登出")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """用户登出"""
    # 在实际应用中，可以将令牌加入黑名单
    # 这里简单返回成功消息
    logger.info(f"用户登出: {current_user.username}")
    return {"message": "登出成功"}

@router.post("/password-reset-request", summary="请求密码重置")
async def password_reset_request(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """请求密码重置"""
    try:
        user = user_service.get_user_by_email(db, request.email)
        
        if not user:
            # 为了安全，即使用户不存在也返回成功
            return {"message": "如果邮箱存在，重置链接已发送"}
        
        # 生成重置令牌
        reset_token = password_manager.generate_password_reset_token(user.id)
        
        # 在实际应用中，这里应该发送邮件
        # 现在只是记录日志
        logger.info(f"密码重置令牌生成: {user.email}, token: {reset_token}")
        
        return {"message": "如果邮箱存在，重置链接已发送"}
        
    except Exception as e:
        logger.error(f"密码重置请求失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="请求失败，请稍后重试"
        )

@router.post("/password-reset", summary="重置密码")
async def password_reset(
    reset_data: PasswordReset,
    db: Session = Depends(get_db)
):
    """重置密码"""
    try:
        # 验证重置令牌
        user_id = password_manager.verify_password_reset_token(reset_data.token)
        
        user = user_service.get_user_by_id(db, user_id)
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户不存在"
            )
        
        # 更新密码
        user_service.update_password(user.id, reset_data.new_password)
        
        logger.info(f"密码重置成功: {user.username}")
        
        return {"message": "密码重置成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"密码重置失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码重置失败"
        )
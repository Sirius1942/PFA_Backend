#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入模块
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.services.user_service import user_service

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_token_from_cookie_or_header(request: Request, token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    """
    从Cookie或Header获取token
    """
    # 优先从Header获取
    if token:
        return token
    
    # 从Cookie获取
    cookie_token = request.cookies.get("access_token")
    return cookie_token

async def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_cookie_or_header)
) -> User:
    """
    获取当前用户
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        # 验证token
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 获取用户
    user = user_service.get_user_by_id(db, user_id=int(user_id))
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前超级用户
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_optional_current_user(
    token: Optional[str] = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    获取可选的当前用户（用于可选认证的接口）
    """
    if not token:
        return None
    
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            return None
            
        user = user_service.get_user_by_username(db, username=username)
        if user and user.is_active:
            return user
    except JWTError:
        pass
    
    return None
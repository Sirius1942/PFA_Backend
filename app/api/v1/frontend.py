#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端页面路由
"""

from fastapi import APIRouter, Request, Depends, Form, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.user_service import user_service
from app.auth.jwt import jwt_manager
from app.core.deps import get_current_user, get_token_from_cookie_or_header
from app.models.user import User
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_cookie_or_header)
) -> Optional[User]:
    """获取当前用户（可选，不抛出异常）"""
    if not token:
        return None
    
    try:
        return await get_current_user(request, db, token)
    except HTTPException:
        return None

@router.get("/dashboard", response_class=HTMLResponse, summary="仪表板页面")
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    """显示用户仪表板"""
    return templates.TemplateResponse("dashboard_new.html", {
        "request": request, 
        "user": current_user,
        "page": "dashboard",
        "title": "仪表板 - 私人金融分析师"
    })

@router.get("/login", response_class=HTMLResponse, summary="登录页面")
async def login_page(request: Request, current_user: Optional[User] = Depends(get_current_user_optional)):
    """显示登录页面"""
    # 如果已经登录，重定向到仪表板
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=302)
    
    return templates.TemplateResponse("login_new.html", {"request": request, "page": "login"})

@router.post("/login", summary="处理登录请求")
async def handle_login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """处理用户登录并重定向"""
    user = user_service.authenticate_user(db, username, password)
    if not user:
        # 登录失败，重新渲染登录页面并显示错误信息
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "用户名或密码错误"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token = jwt_manager.create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )
    response = RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=jwt_manager.access_token_expire_minutes * 60)
    return response

@router.get("/logout", summary="用户登出")
async def logout():
    """清除token并重定向到登录页"""
    response = RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    response.delete_cookie("access_token")
    return response

@router.get("/chat", response_class=HTMLResponse, summary="AI聊天页面")
async def chat_page(request: Request, current_user: User = Depends(get_current_user)):
    """显示AI聊天页面"""
    return templates.TemplateResponse("chat.html", {
        "request": request, 
        "user": current_user,
        "page": "chat",
        "title": "AI助手 - 私人金融分析师"
    })

@router.get("/stocks", response_class=HTMLResponse, summary="股票分析页面")
async def stocks_page(request: Request, current_user: User = Depends(get_current_user)):
    """显示股票分析页面"""
    return templates.TemplateResponse("stocks.html", {
        "request": request, 
        "user": current_user,
        "page": "stocks",
        "title": "股票分析 - 私人金融分析师"
    })

@router.get("/market", response_class=HTMLResponse, summary="市场洞察页面")
async def market_page(request: Request, current_user: User = Depends(get_current_user)):
    """显示市场洞察页面"""
    return templates.TemplateResponse("market.html", {
        "request": request, 
        "user": current_user,
        "page": "market",
        "title": "市场洞察 - 私人金融分析师"
    })

@router.get("/profile", response_class=HTMLResponse, summary="用户资料页面")
async def profile_page(request: Request, current_user: User = Depends(get_current_user)):
    """显示用户资料页面"""
    return templates.TemplateResponse("profile.html", {
        "request": request, 
        "user": current_user,
        "page": "profile",
        "title": "个人资料 - 私人金融分析师"
    })
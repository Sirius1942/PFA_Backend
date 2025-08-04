#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
前端页面路由
"""

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """仪表板主页"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "私人金融分析师",
        "page": "dashboard"
    })

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """登录页面"""
    return templates.TemplateResponse("login.html", {
        "request": request,
        "title": "用户登录",
        "page": "login"
    })

@router.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request):
    """AI聊天页面"""
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "title": "AI助手聊天",
        "page": "chat"
    })

@router.get("/stocks", response_class=HTMLResponse)
async def stocks_page(request: Request):
    """股票分析页面"""
    return templates.TemplateResponse("stocks.html", {
        "request": request,
        "title": "股票分析",
        "page": "stocks"
    })

@router.get("/market", response_class=HTMLResponse)
async def market_page(request: Request):
    """市场洞察页面"""
    return templates.TemplateResponse("market.html", {
        "request": request,
        "title": "市场洞察",
        "page": "market"
    })

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    """用户资料页面"""
    return templates.TemplateResponse("profile.html", {
        "request": request,
        "title": "用户资料",
        "page": "profile"
    })
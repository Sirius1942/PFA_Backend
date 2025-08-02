#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
私人金融分析师 - FastAPI后端主应用

功能特性：
1. 用户认证和授权（RBAC）
2. 股票数据查询和分析
3. 金融AI助手
4. 权限管理
5. RESTful API

作者: Assistant
日期: 2024
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn
import logging
from pathlib import Path

# 导入应用模块
from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1.router import api_router
# from app.auth.middleware import AuthMiddleware
# from app.core.logging import setup_logging

# 设置日志
# setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    logger.info("🚀 启动私人金融分析师后端服务...")
    
    # 创建数据库表
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ 数据库表创建成功")
    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        raise
    
    yield
    
    # 关闭时执行
    logger.info("🛑 关闭私人金融分析师后端服务")

# 创建FastAPI应用
app = FastAPI(
    title="私人金融分析师API",
    description="基于AI的个人金融分析和投资助手",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 信任主机中间件
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# 认证中间件
# app.add_middleware(AuthMiddleware)

# 注册路由
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "私人金融分析师API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "private-financial-analyst",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
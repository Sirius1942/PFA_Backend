#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API v1 路由汇总
"""

from fastapi import APIRouter

# 导入各模块路由
from .auth import router as auth_router
from .users import router as users_router
from .stocks import router as stocks_router
from .assistant import router as assistant_router
from .data_collection import router as data_collection_router
from .system import router as system_router

# from .admin import router as admin_router

# 创建主路由
api_router = APIRouter()

# 注册子路由
api_router.include_router(
    auth_router,
    prefix="/auth",
    tags=["认证"]
)

api_router.include_router(
    users_router,
    prefix="/users",
    tags=["用户管理"]
)

api_router.include_router(
    stocks_router,
    prefix="/stocks",
    tags=["股票数据"]
)

api_router.include_router(
    assistant_router,
    prefix="/assistant",
    tags=["AI助手"]
)

api_router.include_router(
    data_collection_router,
    prefix="/data",
    tags=["数据采集"]
)

api_router.include_router(
    system_router,
    tags=["系统管理"]
)

# api_router.include_router(
#     admin_router,
#     prefix="/admin",
#     tags=["系统管理"]
# )


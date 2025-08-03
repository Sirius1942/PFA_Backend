#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据采集管理API
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from app.core.database import get_db
from app.models.user import User
from app.services.stock_service import stock_service
from app.core.deps import get_current_user
from app.auth.permissions import require_permission, Permissions, require_admin
from pydantic import BaseModel

router = APIRouter(tags=["数据采集"])

class CollectionRequest(BaseModel):
    stock_codes: List[str]
    include_kline: bool = True
    include_realtime: bool = True
    include_info: bool = True

class CollectionResponse(BaseModel):
    status: str
    message: str
    details: Dict[str, Any]

@router.post("/collect/stocks", response_model=CollectionResponse)
@require_admin()
async def collect_stock_data(
    request: CollectionRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """采集指定股票的数据"""
    try:
        if len(request.stock_codes) > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多采集100只股票"
            )
        
        # 异步采集数据
        background_tasks.add_task(
            _collect_stocks_background,
            db, request.stock_codes, request.include_kline, 
            request.include_realtime, request.include_info
        )
        
        return CollectionResponse(
            status="success",
            message=f"开始采集 {len(request.stock_codes)} 只股票的数据",
            details={
                "stock_count": len(request.stock_codes),
                "include_kline": request.include_kline,
                "include_realtime": request.include_realtime,
                "include_info": request.include_info,
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动数据采集失败: {str(e)}"
        )

@router.post("/collect/realtime", response_model=CollectionResponse)
@require_admin()
async def collect_realtime_quotes(
    stock_codes: List[str],
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """采集实时行情数据"""
    try:
        if len(stock_codes) > 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="一次最多采集200只股票的实时行情"
            )
        
        # 异步采集实时行情
        background_tasks.add_task(_collect_realtime_background, db, stock_codes)
        
        return CollectionResponse(
            status="success",
            message=f"开始采集 {len(stock_codes)} 只股票的实时行情",
            details={
                "stock_count": len(stock_codes),
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"启动实时行情采集失败: {str(e)}"
        )

@router.post("/collect/search", response_model=List[Dict[str, Any]])
@require_permission(Permissions.VIEW_STOCKS)
async def search_stocks_external(
    keyword: str,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """从外部API搜索股票"""
    try:
        async with stock_service:
            results = await stock_service.search_stocks_from_api(keyword, limit)
        
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索股票失败: {str(e)}"
        )

@router.post("/collect/update-watchlist")
@require_admin()
async def update_watchlist_stocks(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新自选股数据（调试模式：3只股票）"""
    try:
        # 获取调试用自选股代码
        debug_codes = stock_service.get_debug_watchlist_stocks(db)
        
        background_tasks.add_task(
            _collect_stocks_background, db, debug_codes, True, True, True
        )
        
        return CollectionResponse(
            status="success",
            message=f"开始更新 {len(debug_codes)} 只自选股数据（调试模式）",
            details={
                "stock_codes": debug_codes,
                "debug_mode": True,
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新自选股失败: {str(e)}"
        )

async def _collect_stocks_background(
    db: Session, 
    stock_codes: List[str], 
    include_kline: bool, 
    include_realtime: bool, 
    include_info: bool
):
    """后台数据采集任务"""
    try:
        async with stock_service:
            results = {"success": [], "failed": []}
            
            for stock_code in stock_codes:
                try:
                    # 采集股票基本信息
                    if include_info:
                        await stock_service.update_stock_info(db, stock_code)
                    
                    # 采集实时行情
                    if include_realtime:
                        await stock_service.update_realtime_quote(db, stock_code)
                    
                    # 采集K线数据
                    if include_kline:
                        await stock_service.update_kline_data(db, stock_code, "1d", 100)
                    
                    results["success"].append(stock_code)
                    
                except Exception as e:
                    results["failed"].append({"code": stock_code, "error": str(e)})
                
                # 避免请求过于频繁
                await asyncio.sleep(0.1)
        
        print(f"数据采集完成: 成功 {len(results['success'])}, 失败 {len(results['failed'])}")
        
    except Exception as e:
        print(f"后台数据采集任务失败: {e}")

async def _collect_realtime_background(db: Session, stock_codes: List[str]):
    """后台实时行情采集任务"""
    try:
        async with stock_service:
            results = await stock_service.batch_update_quotes(db, stock_codes)
        
        success_count = sum(1 for success in results.values() if success)
        print(f"实时行情采集完成: 成功 {success_count}/{len(stock_codes)}")
        
    except Exception as e:
        print(f"后台实时行情采集任务失败: {e}")
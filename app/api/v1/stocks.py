from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
import asyncio

from app.core.database import get_db
from app.models.user import User
from app.models.stock import StockInfo, KlineData, RealtimeQuotes, UserWatchlist
from app.core.deps import get_current_user
from app.auth.permissions import require_permission, Permissions
from pydantic import BaseModel
from decimal import Decimal

router = APIRouter(prefix="/stocks", tags=["股票数据"])

# Pydantic模型
class StockInfoResponse(BaseModel):
    id: int
    code: str
    name: str
    market: str
    industry: Optional[str] = None
    sector: Optional[str] = None
    listing_date: Optional[datetime] = None
    total_shares: Optional[int] = None
    market_cap: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RealtimeQuoteResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    current_price: Decimal
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    prev_close: Decimal
    volume: int
    turnover: Decimal
    change_amount: Decimal
    change_percent: Decimal
    timestamp: datetime
    
    class Config:
        from_attributes = True

class KlineDataResponse(BaseModel):
    id: int
    stock_code: str
    period: str
    timestamp: datetime
    open_price: Decimal
    high_price: Decimal
    low_price: Decimal
    close_price: Decimal
    volume: int
    turnover: Decimal
    change_amount: Decimal
    change_percent: Decimal
    
    class Config:
        from_attributes = True

class WatchlistResponse(BaseModel):
    id: int
    stock_code: str
    stock_name: str
    added_at: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class WatchlistAdd(BaseModel):
    stock_code: str
    notes: Optional[str] = None

class WatchlistUpdate(BaseModel):
    notes: Optional[str] = None

@router.get("/search", response_model=List[StockInfoResponse])
@require_permission(Permissions.VIEW_STOCKS)
async def search_stocks(
    q: str = Query(..., min_length=1, description="搜索关键词（股票代码或名称）"),
    limit: int = Query(20, ge=1, le=100),
    market: Optional[str] = Query(None, description="市场筛选（SH/SZ/BJ）"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """搜索股票"""
    query = db.query(StockInfo).filter(StockInfo.is_active == True)
    
    # 关键词搜索
    search_filter = or_(
        StockInfo.code.contains(q),
        StockInfo.name.contains(q)
    )
    query = query.filter(search_filter)
    
    # 市场筛选
    if market:
        query = query.filter(StockInfo.market == market.upper())
    
    # 行业筛选
    if industry:
        query = query.filter(StockInfo.industry == industry)
    
    stocks = query.limit(limit).all()
    return stocks

@router.get("/info/{stock_code}", response_model=StockInfoResponse)
@require_permission(Permissions.VIEW_STOCKS)
async def get_stock_info(
    stock_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取股票基本信息"""
    stock = db.query(StockInfo).filter(
        and_(StockInfo.code == stock_code, StockInfo.is_active == True)
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="股票不存在"
        )
    
    return stock

@router.get("/realtime/{stock_code}", response_model=RealtimeQuoteResponse)
@require_permission(Permissions.VIEW_REALTIME_DATA)
async def get_realtime_quote(
    stock_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取股票实时行情"""
    quote = db.query(RealtimeQuotes).filter(
        RealtimeQuotes.stock_code == stock_code
    ).order_by(desc(RealtimeQuotes.timestamp)).first()
    
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="未找到实时行情数据"
        )
    
    return quote

@router.get("/realtime/batch", response_model=List[RealtimeQuoteResponse])
@require_permission(Permissions.VIEW_REALTIME_DATA)
async def get_batch_realtime_quotes(
    stock_codes: str = Query(..., description="股票代码列表，逗号分隔"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """批量获取股票实时行情"""
    codes = [code.strip() for code in stock_codes.split(',') if code.strip()]
    
    if len(codes) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="一次最多查询50只股票"
        )
    
    # 获取每只股票的最新行情
    quotes = []
    for code in codes:
        quote = db.query(RealtimeQuotes).filter(
            RealtimeQuotes.stock_code == code
        ).order_by(desc(RealtimeQuotes.timestamp)).first()
        
        if quote:
            quotes.append(quote)
    
    return quotes

@router.get("/kline/{stock_code}", response_model=List[KlineDataResponse])
@require_permission(Permissions.VIEW_STOCKS)
async def get_kline_data(
    stock_code: str,
    period: str = Query("1d", description="K线周期（1m/5m/15m/30m/1h/1d/1w/1M）"),
    start_date: Optional[datetime] = Query(None, description="开始日期"),
    end_date: Optional[datetime] = Query(None, description="结束日期"),
    limit: int = Query(100, ge=1, le=1000, description="返回数据条数"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取K线数据"""
    query = db.query(KlineData).filter(
        and_(
            KlineData.stock_code == stock_code,
            KlineData.period == period
        )
    )
    
    # 日期范围筛选
    if start_date:
        query = query.filter(KlineData.timestamp >= start_date)
    
    if end_date:
        query = query.filter(KlineData.timestamp <= end_date)
    
    # 如果没有指定日期范围，默认获取最近的数据
    if not start_date and not end_date:
        query = query.order_by(desc(KlineData.timestamp))
    else:
        query = query.order_by(KlineData.timestamp)
    
    kline_data = query.limit(limit).all()
    
    # 如果是按时间倒序查询，需要重新排序
    if not start_date and not end_date:
        kline_data.reverse()
    
    return kline_data

@router.get("/watchlist", response_model=List[WatchlistResponse])
@require_permission(Permissions.MANAGE_WATCHLIST)
async def get_user_watchlist(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户自选股列表"""
    watchlist = db.query(UserWatchlist).filter(
        UserWatchlist.user_id == current_user.id
    ).order_by(desc(UserWatchlist.added_at)).all()
    
    return watchlist

@router.post("/watchlist", response_model=WatchlistResponse)
@require_permission(Permissions.MANAGE_WATCHLIST)
async def add_to_watchlist(
    watchlist_data: WatchlistAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加股票到自选股"""
    # 检查股票是否存在
    stock = db.query(StockInfo).filter(
        and_(
            StockInfo.code == watchlist_data.stock_code,
            StockInfo.is_active == True
        )
    ).first()
    
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="股票不存在"
        )
    
    # 检查是否已在自选股中
    existing = db.query(UserWatchlist).filter(
        and_(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.stock_code == watchlist_data.stock_code
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="股票已在自选股中"
        )
    
    # 添加到自选股
    watchlist_item = UserWatchlist(
        user_id=current_user.id,
        stock_code=watchlist_data.stock_code,
        stock_name=stock.name,
        notes=watchlist_data.notes
    )
    
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    
    return watchlist_item

@router.put("/watchlist/{stock_code}", response_model=WatchlistResponse)
@require_permission(Permissions.MANAGE_WATCHLIST)
async def update_watchlist_item(
    stock_code: str,
    update_data: WatchlistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新自选股备注"""
    watchlist_item = db.query(UserWatchlist).filter(
        and_(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.stock_code == stock_code
        )
    ).first()
    
    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自选股不存在"
        )
    
    if update_data.notes is not None:
        watchlist_item.notes = update_data.notes
    
    db.commit()
    db.refresh(watchlist_item)
    
    return watchlist_item

@router.delete("/watchlist/{stock_code}")
@require_permission(Permissions.MANAGE_WATCHLIST)
async def remove_from_watchlist(
    stock_code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """从自选股中移除股票"""
    watchlist_item = db.query(UserWatchlist).filter(
        and_(
            UserWatchlist.user_id == current_user.id,
            UserWatchlist.stock_code == stock_code
        )
    ).first()
    
    if not watchlist_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="自选股不存在"
        )
    
    db.delete(watchlist_item)
    db.commit()
    
    return {"message": "已从自选股中移除"}

@router.get("/markets")
@require_permission(Permissions.VIEW_STOCKS)
async def get_markets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取市场列表"""
    markets = db.query(StockInfo.market).distinct().all()
    return [market[0] for market in markets if market[0]]

@router.get("/industries")
@require_permission(Permissions.VIEW_STOCKS)
async def get_industries(
    market: Optional[str] = Query(None, description="市场筛选"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取行业列表"""
    query = db.query(StockInfo.industry).filter(StockInfo.industry.isnot(None))
    
    if market:
        query = query.filter(StockInfo.market == market.upper())
    
    industries = query.distinct().all()
    return [industry[0] for industry in industries if industry[0]]

@router.get("/stats/market-overview")
@require_permission(Permissions.VIEW_STOCKS)
async def get_market_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取市场概览统计"""
    # 获取各市场股票数量
    market_stats = db.query(
        StockInfo.market,
        db.func.count(StockInfo.id).label('count')
    ).filter(StockInfo.is_active == True).group_by(StockInfo.market).all()
    
    # 获取行业分布
    industry_stats = db.query(
        StockInfo.industry,
        db.func.count(StockInfo.id).label('count')
    ).filter(
        and_(StockInfo.is_active == True, StockInfo.industry.isnot(None))
    ).group_by(StockInfo.industry).order_by(desc('count')).limit(10).all()
    
    return {
        "market_distribution": [
            {"market": stat.market, "count": stat.count}
            for stat in market_stats
        ],
        "top_industries": [
            {"industry": stat.industry, "count": stat.count}
            for stat in industry_stats
        ],
        "total_stocks": sum(stat.count for stat in market_stats)
    }
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

router = APIRouter(tags=["股票数据"])

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
    created_at: datetime
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True

class WatchlistAdd(BaseModel):
    stock_code: str
    notes: Optional[str] = None

class WatchlistUpdate(BaseModel):
    notes: Optional[str] = None

# 看板数据响应模型
class DashboardStockQuote(BaseModel):
    """看板股票行情数据"""
    stock_code: str
    stock_name: str
    current_price: float
    change_amount: float
    change_percent: float
    volume: int
    amount: float
    quote_time: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DashboardMarketSummary(BaseModel):
    """看板市场概览"""
    total_stocks: int = 0
    up_count: int = 0
    down_count: int = 0
    flat_count: int = 0
    up_ratio: float = 0.0
    
class DashboardResponse(BaseModel):
    """看板数据响应"""
    user_id: int
    watchlist_stocks: List[DashboardStockQuote]
    market_summary: DashboardMarketSummary
    last_updated: datetime

@router.get("/search", response_model=List[StockInfoResponse])
@require_permission(Permissions.VIEW_STOCKS)
async def search_stocks(
    q: str = Query(..., min_length=1, description="搜索关键词（股票代码或名称）"),
    limit: int = Query(20, ge=1, le=100),
    market: Optional[str] = Query(None, description="市场筛选（SH/SZ/BJ）"),
    industry: Optional[str] = Query(None, description="行业筛选"),
    auto_fetch: bool = Query(True, description="是否自动从外部API获取股票数据"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """股票搜索 - 优先从本地数据库搜索，如果没有结果则从外部API获取"""
    
    # 1. 先从本地数据库搜索
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
    
    local_stocks = query.limit(limit).all()
    
    # 2. 如果本地没有结果且允许自动获取，则从外部API搜索
    if not local_stocks and auto_fetch:
        try:
            from app.services.stock_service import stock_service
            
            async with stock_service:
                external_results = await stock_service.search_stocks_from_api(q, limit)
                
                # 将外部结果转换并保存到数据库
                for result in external_results:
                    try:
                        # 检查是否已存在
                        existing = db.query(StockInfo).filter(StockInfo.code == result['code']).first()
                        if not existing:
                            # 获取完整股票信息
                            stock_detail = await stock_service.fetch_stock_info(result['code'])
                            if stock_detail:
                                new_stock = StockInfo(
                                    code=stock_detail['code'],
                                    name=stock_detail['name'],
                                    market=stock_detail['market'],
                                    industry=stock_detail.get('industry'),
                                    sector=stock_detail.get('sector'),
                                    listing_date=stock_detail.get('listing_date'),
                                    total_shares=stock_detail.get('total_shares'),
                                    market_cap=stock_detail.get('market_cap'),
                                    is_active=True
                                )
                                db.add(new_stock)
                                db.commit()
                                db.refresh(new_stock)
                                local_stocks.append(new_stock)
                    except Exception as e:
                        # 单个股票添加失败不影响其他
                        print(f"添加股票 {result['code']} 失败: {e}")
                        continue
                        
        except Exception as e:
            # 外部API调用失败，返回空结果但不报错
            print(f"外部API搜索失败: {e}")
    
    return local_stocks

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
    # 联合查询获取自选股和股票信息
    watchlist_with_names = db.query(
        UserWatchlist,
        StockInfo.name.label('stock_name')
    ).outerjoin(
        StockInfo, UserWatchlist.stock_code == StockInfo.code
    ).filter(
        UserWatchlist.user_id == current_user.id
    ).order_by(desc(UserWatchlist.created_at)).all()
    
    # 构造响应数据
    result = []
    for watchlist_item, stock_name in watchlist_with_names:
        result.append({
            "id": watchlist_item.id,
            "stock_code": watchlist_item.stock_code,
            "stock_name": stock_name or f"股票{watchlist_item.stock_code}",
            "created_at": watchlist_item.created_at,
            "notes": watchlist_item.notes
        })
    
    return result

@router.post("/watchlist", response_model=WatchlistResponse)
@require_permission(Permissions.MANAGE_WATCHLIST)
async def add_to_watchlist(
    watchlist_data: WatchlistAdd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """添加股票到自选股 - 如果股票不存在会自动从外部API获取"""
    
    # 检查股票是否存在
    stock = db.query(StockInfo).filter(
        and_(
            StockInfo.code == watchlist_data.stock_code,
            StockInfo.is_active == True
        )
    ).first()
    
    # 如果股票不存在，尝试从外部API获取
    if not stock:
        try:
            from app.services.stock_service import stock_service
            
            async with stock_service:
                # 获取股票详细信息
                stock_detail = await stock_service.fetch_stock_info(watchlist_data.stock_code)
                
                if stock_detail:
                    # 创建新的股票记录
                    stock = StockInfo(
                        code=stock_detail['code'],
                        name=stock_detail['name'],
                        market=stock_detail['market'],
                        industry=stock_detail.get('industry'),
                        sector=stock_detail.get('sector'),
                        listing_date=stock_detail.get('listing_date'),
                        total_shares=stock_detail.get('total_shares'),
                        market_cap=stock_detail.get('market_cap'),
                        is_active=True
                    )
                    db.add(stock)
                    db.commit()
                    db.refresh(stock)
                    
        except Exception as e:
            print(f"从外部API获取股票信息失败: {e}")
    
    # 如果仍然没有找到股票
    if not stock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="股票不存在或无法获取股票信息"
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
        notes=watchlist_data.notes
    )
    
    db.add(watchlist_item)
    db.commit()
    db.refresh(watchlist_item)
    
    # 返回包含股票名称的响应
    return {
        "id": watchlist_item.id,
        "stock_code": watchlist_item.stock_code,
        "stock_name": stock.name,
        "created_at": watchlist_item.created_at,
        "notes": watchlist_item.notes
    }

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
    
    # 获取股票名称
    stock = db.query(StockInfo).filter(StockInfo.code == stock_code).first()
    stock_name = stock.name if stock else f"股票{stock_code}"
    
    # 返回包含股票名称的响应
    return {
        "id": watchlist_item.id,
        "stock_code": watchlist_item.stock_code,
        "stock_name": stock_name,
        "created_at": watchlist_item.created_at,
        "notes": watchlist_item.notes
    }

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

@router.get("/dashboard", response_model=DashboardResponse)
@require_permission(Permissions.VIEW_STOCKS)
async def get_dashboard_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取用户个性化看板数据"""
    try:
        # 获取用户自选股列表
        user_watchlist = db.query(UserWatchlist).filter(
            UserWatchlist.user_id == current_user.id
        ).all()
        
        # 如果用户没有自选股，返回空的看板数据
        if not user_watchlist:
            return DashboardResponse(
                user_id=current_user.id,
                watchlist_stocks=[],
                market_summary=DashboardMarketSummary(),
                last_updated=datetime.utcnow()
            )
        
        # 获取自选股代码列表
        stock_codes = [item.stock_code for item in user_watchlist]
        
        # 获取自选股的最新实时行情
        quotes = db.query(RealtimeQuotes).filter(
            RealtimeQuotes.code.in_(stock_codes)
        ).order_by(desc(RealtimeQuotes.quote_time)).all()
        
        # 按股票代码去重，保留最新的行情
        latest_quotes = {}
        for quote in quotes:
            if quote.code not in latest_quotes:
                latest_quotes[quote.code] = quote
        
        # 构造看板股票行情数据
        dashboard_stocks = []
        for stock_code in stock_codes:
            quote = latest_quotes.get(stock_code)
            if quote:
                dashboard_stocks.append(DashboardStockQuote(
                    stock_code=quote.code,
                    stock_name=quote.name,
                    current_price=float(quote.current_price),
                    change_amount=float(quote.change_amount),
                    change_percent=float(quote.change_percent),
                    volume=int(quote.volume),
                    amount=float(quote.amount),
                    quote_time=quote.quote_time
                ))
        
        # 计算市场概览（基于用户自选股）
        total_stocks = len(dashboard_stocks)
        up_count = sum(1 for stock in dashboard_stocks if stock.change_percent > 0)
        down_count = sum(1 for stock in dashboard_stocks if stock.change_percent < 0)
        flat_count = total_stocks - up_count - down_count
        up_ratio = (up_count / total_stocks * 100) if total_stocks > 0 else 0.0
        
        market_summary = DashboardMarketSummary(
            total_stocks=total_stocks,
            up_count=up_count,
            down_count=down_count,
            flat_count=flat_count,
            up_ratio=round(up_ratio, 2)
        )
        
        return DashboardResponse(
            user_id=current_user.id,
            watchlist_stocks=dashboard_stocks,
            market_summary=market_summary,
            last_updated=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取看板数据失败: {str(e)}"
        )
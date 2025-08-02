from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
from decimal import Decimal

from app.models.stock import StockInfo, KlineData, RealtimeQuotes, UserWatchlist
from app.core.config import settings
from loguru import logger

class StockDataService:
    """股票数据服务类"""
    
    def __init__(self):
        self.eastmoney_base_url = settings.EASTMONEY_API_BASE
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def fetch_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取股票基本信息"""
        try:
            # 这里应该调用真实的股票API
            # 现在返回模拟数据
            return {
                "code": stock_code,
                "name": f"股票{stock_code}",
                "market": "SH" if stock_code.startswith("6") else "SZ",
                "industry": "科技",
                "sector": "软件服务",
                "listing_date": "2020-01-01",
                "total_shares": 1000000000,
                "market_cap": 50000000000
            }
        except Exception as e:
            logger.error(f"获取股票信息失败 {stock_code}: {e}")
            return None
    
    async def fetch_realtime_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """获取实时行情数据"""
        try:
            # 模拟实时行情数据
            import random
            base_price = 10.0 + random.uniform(-2, 2)
            change_percent = random.uniform(-5, 5)
            
            return {
                "stock_code": stock_code,
                "current_price": round(base_price, 2),
                "open_price": round(base_price * 0.98, 2),
                "high_price": round(base_price * 1.05, 2),
                "low_price": round(base_price * 0.95, 2),
                "prev_close": round(base_price / (1 + change_percent/100), 2),
                "volume": random.randint(1000000, 10000000),
                "turnover": round(base_price * random.randint(1000000, 10000000), 2),
                "change_percent": round(change_percent, 2),
                "timestamp": datetime.utcnow()
            }
        except Exception as e:
            logger.error(f"获取实时行情失败 {stock_code}: {e}")
            return None
    
    async def fetch_kline_data(self, stock_code: str, period: str = "1d", count: int = 100) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            # 模拟K线数据
            import random
            kline_data = []
            base_price = 10.0
            
            for i in range(count):
                # 生成模拟的K线数据
                open_price = base_price + random.uniform(-0.5, 0.5)
                close_price = open_price + random.uniform(-1, 1)
                high_price = max(open_price, close_price) + random.uniform(0, 0.5)
                low_price = min(open_price, close_price) - random.uniform(0, 0.5)
                
                kline_data.append({
                    "stock_code": stock_code,
                    "period": period,
                    "timestamp": datetime.utcnow() - timedelta(days=count-i),
                    "open_price": round(open_price, 2),
                    "high_price": round(high_price, 2),
                    "low_price": round(low_price, 2),
                    "close_price": round(close_price, 2),
                    "volume": random.randint(100000, 1000000),
                    "turnover": round(close_price * random.randint(100000, 1000000), 2)
                })
                
                base_price = close_price
            
            return kline_data
        except Exception as e:
            logger.error(f"获取K线数据失败 {stock_code}: {e}")
            return []
    
    async def update_stock_info(self, db: Session, stock_code: str) -> Optional[StockInfo]:
        """更新股票基本信息到数据库"""
        try:
            stock_data = await self.fetch_stock_info(stock_code)
            if not stock_data:
                return None
            
            # 查找现有记录
            stock = db.query(StockInfo).filter(StockInfo.code == stock_code).first()
            
            if stock:
                # 更新现有记录
                stock.name = stock_data["name"]
                stock.market = stock_data["market"]
                stock.industry = stock_data.get("industry")
                stock.sector = stock_data.get("sector")
                stock.total_shares = stock_data.get("total_shares")
                stock.market_cap = stock_data.get("market_cap")
                stock.updated_at = datetime.utcnow()
            else:
                # 创建新记录
                stock = StockInfo(
                    code=stock_code,
                    name=stock_data["name"],
                    market=stock_data["market"],
                    industry=stock_data.get("industry"),
                    sector=stock_data.get("sector"),
                    listing_date=datetime.fromisoformat(stock_data["listing_date"]) if stock_data.get("listing_date") else None,
                    total_shares=stock_data.get("total_shares"),
                    market_cap=stock_data.get("market_cap"),
                    is_active=True
                )
                db.add(stock)
            
            db.commit()
            db.refresh(stock)
            return stock
            
        except Exception as e:
            logger.error(f"更新股票信息失败 {stock_code}: {e}")
            db.rollback()
            return None
    
    async def update_realtime_quote(self, db: Session, stock_code: str) -> Optional[RealtimeQuotes]:
        """更新实时行情到数据库"""
        try:
            quote_data = await self.fetch_realtime_quote(stock_code)
            if not quote_data:
                return None
            
            # 获取股票名称
            stock = db.query(StockInfo).filter(StockInfo.code == stock_code).first()
            stock_name = stock.name if stock else f"股票{stock_code}"
            
            # 计算涨跌额
            current_price = Decimal(str(quote_data["current_price"]))
            prev_close = Decimal(str(quote_data["prev_close"]))
            change_amount = current_price - prev_close
            
            # 创建新的行情记录
            quote = RealtimeQuotes(
                stock_code=stock_code,
                stock_name=stock_name,
                current_price=current_price,
                open_price=Decimal(str(quote_data["open_price"])),
                high_price=Decimal(str(quote_data["high_price"])),
                low_price=Decimal(str(quote_data["low_price"])),
                prev_close=prev_close,
                volume=quote_data["volume"],
                turnover=Decimal(str(quote_data["turnover"])),
                change_amount=change_amount,
                change_percent=Decimal(str(quote_data["change_percent"])),
                timestamp=quote_data["timestamp"]
            )
            
            db.add(quote)
            db.commit()
            db.refresh(quote)
            return quote
            
        except Exception as e:
            logger.error(f"更新实时行情失败 {stock_code}: {e}")
            db.rollback()
            return None
    
    async def update_kline_data(self, db: Session, stock_code: str, period: str = "1d", count: int = 100) -> int:
        """更新K线数据到数据库"""
        try:
            kline_data_list = await self.fetch_kline_data(stock_code, period, count)
            if not kline_data_list:
                return 0
            
            updated_count = 0
            
            for kline_data in kline_data_list:
                # 检查是否已存在相同时间的数据
                existing = db.query(KlineData).filter(
                    and_(
                        KlineData.stock_code == stock_code,
                        KlineData.period == period,
                        KlineData.timestamp == kline_data["timestamp"]
                    )
                ).first()
                
                if existing:
                    # 更新现有数据
                    existing.open_price = Decimal(str(kline_data["open_price"]))
                    existing.high_price = Decimal(str(kline_data["high_price"]))
                    existing.low_price = Decimal(str(kline_data["low_price"]))
                    existing.close_price = Decimal(str(kline_data["close_price"]))
                    existing.volume = kline_data["volume"]
                    existing.turnover = Decimal(str(kline_data["turnover"]))
                else:
                    # 创建新数据
                    open_price = Decimal(str(kline_data["open_price"]))
                    close_price = Decimal(str(kline_data["close_price"]))
                    
                    kline = KlineData(
                        stock_code=stock_code,
                        period=period,
                        timestamp=kline_data["timestamp"],
                        open_price=open_price,
                        high_price=Decimal(str(kline_data["high_price"])),
                        low_price=Decimal(str(kline_data["low_price"])),
                        close_price=close_price,
                        volume=kline_data["volume"],
                        turnover=Decimal(str(kline_data["turnover"])),
                        change_amount=close_price - open_price,
                        change_percent=((close_price - open_price) / open_price * 100) if open_price > 0 else Decimal('0')
                    )
                    db.add(kline)
                
                updated_count += 1
            
            db.commit()
            return updated_count
            
        except Exception as e:
            logger.error(f"更新K线数据失败 {stock_code}: {e}")
            db.rollback()
            return 0
    
    async def batch_update_quotes(self, db: Session, stock_codes: List[str]) -> Dict[str, bool]:
        """批量更新股票行情"""
        results = {}
        
        # 限制并发数量
        semaphore = asyncio.Semaphore(10)
        
        async def update_single_quote(stock_code: str):
            async with semaphore:
                try:
                    quote = await self.update_realtime_quote(db, stock_code)
                    return stock_code, quote is not None
                except Exception as e:
                    logger.error(f"批量更新行情失败 {stock_code}: {e}")
                    return stock_code, False
        
        # 并发更新
        tasks = [update_single_quote(code) for code in stock_codes]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in task_results:
            if isinstance(result, tuple):
                stock_code, success = result
                results[stock_code] = success
            else:
                logger.error(f"批量更新任务异常: {result}")
        
        return results
    
    def get_popular_stocks(self, db: Session, limit: int = 20) -> List[StockInfo]:
        """获取热门股票（基于自选股数量）"""
        try:
            # 统计自选股数量最多的股票
            popular_stocks = db.query(
                StockInfo,
                func.count(UserWatchlist.id).label('watchlist_count')
            ).outerjoin(
                UserWatchlist, StockInfo.code == UserWatchlist.stock_code
            ).filter(
                StockInfo.is_active == True
            ).group_by(
                StockInfo.id
            ).order_by(
                desc('watchlist_count')
            ).limit(limit).all()
            
            return [stock[0] for stock in popular_stocks]
            
        except Exception as e:
            logger.error(f"获取热门股票失败: {e}")
            return []
    
    def search_stocks(self, db: Session, keyword: str, market: Optional[str] = None, limit: int = 20) -> List[StockInfo]:
        """搜索股票"""
        try:
            query = db.query(StockInfo).filter(
                and_(
                    StockInfo.is_active == True,
                    or_(
                        StockInfo.code.contains(keyword),
                        StockInfo.name.contains(keyword)
                    )
                )
            )
            
            if market:
                query = query.filter(StockInfo.market == market.upper())
            
            return query.limit(limit).all()
            
        except Exception as e:
            logger.error(f"搜索股票失败: {e}")
            return []
    
    def get_market_summary(self, db: Session) -> Dict[str, Any]:
        """获取市场概况"""
        try:
            # 统计各市场股票数量
            market_stats = db.query(
                StockInfo.market,
                func.count(StockInfo.id).label('count')
            ).filter(
                StockInfo.is_active == True
            ).group_by(
                StockInfo.market
            ).all()
            
            # 统计行业分布
            industry_stats = db.query(
                StockInfo.industry,
                func.count(StockInfo.id).label('count')
            ).filter(
                and_(
                    StockInfo.is_active == True,
                    StockInfo.industry.isnot(None)
                )
            ).group_by(
                StockInfo.industry
            ).order_by(
                desc('count')
            ).limit(10).all()
            
            return {
                "market_distribution": {
                    stat.market: stat.count for stat in market_stats
                },
                "top_industries": [
                    {"industry": stat.industry, "count": stat.count}
                    for stat in industry_stats
                ],
                "total_stocks": sum(stat.count for stat in market_stats),
                "last_updated": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"获取市场概况失败: {e}")
            return {}

# 创建全局服务实例
stock_service = StockDataService()
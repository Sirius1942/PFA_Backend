from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func
from datetime import datetime, timedelta
import asyncio
import aiohttp
import json
import re
import pandas as pd
from decimal import Decimal
from urllib.parse import quote

from app.models.stock import StockInfo, KlineData, RealtimeQuotes, UserWatchlist
from app.core.config import settings
from loguru import logger

class StockDataService:
    """股票数据服务类"""
    
    def __init__(self):
        self.eastmoney_base_url = getattr(settings, 'EASTMONEY_BASE_URL', 'https://push2.eastmoney.com')
        self.quote_url = getattr(settings, 'EASTMONEY_QUOTE_URL', 'https://quote.eastmoney.com')
        self.kline_url = getattr(settings, 'EASTMONEY_KLINE_URL', 'https://push2his.eastmoney.com')
        self.search_url = getattr(settings, 'EASTMONEY_SEARCH_URL', 'https://searchapi.eastmoney.com')
        self.session = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        # 创建SSL上下文，禁用证书验证以避免网络问题
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=30)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout,
            headers=headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def fetch_stock_info(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """从东方财富获取股票基本信息"""
        try:
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                timeout = aiohttp.ClientTimeout(total=30)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                self.session = aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    headers=headers
                )
            
            # 使用搜索API获取股票信息，因为它更稳定
            search_results = await self.search_stocks_from_api(stock_code, 10)
            
            # 找到精确匹配的股票代码
            target_stock = None
            for stock in search_results:
                if stock['code'] == stock_code:
                    # 优先选择主板股票（market为1或0）
                    if str(stock['market']) in ['1', '0']:
                        target_stock = stock
                        break
                    elif target_stock is None:
                        target_stock = stock
            
            if target_stock:
                # 确定市场
                market_map = {'1': 'SH', '0': 'SZ', '90': 'BJ'}
                market = market_map.get(str(target_stock['market']), 'SZ')
                
                return {
                    "code": stock_code,
                    "name": target_stock['name'],
                    "market": market,
                    "industry": None,  # 暂时不获取详细行业信息
                    "sector": None,
                    "listing_date": None,
                    "total_shares": None,
                    "market_cap": None
                }
            
            logger.warning(f"未能从搜索结果中找到股票: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"获取股票信息失败 {stock_code}: {e}")
            return None
    
    async def fetch_realtime_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """从东方财富获取实时行情数据"""
        try:
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                timeout = aiohttp.ClientTimeout(total=30)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                self.session = aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    headers=headers
                )
            
            # 确定市场代码
            market_code = self._get_market_code(stock_code)
            
            # 东方财富实时行情API
            url = f"{self.eastmoney_base_url}/api/qt/stock/get"
            params = {
                "secid": f"{market_code}.{stock_code}",
                "fltt": "2",
                "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f57,f58,f60,f169,f170"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("rc") == 0 and data.get("data"):
                        quote_data = data["data"]
                        
                        current_price = quote_data.get("f43", 0)        # 当前价
                        prev_close = quote_data.get("f60", 0)            # 昨收价
                        open_price = quote_data.get("f46", 0)            # 开盘价
                        high_price = quote_data.get("f44", 0)            # 最高价
                        low_price = quote_data.get("f45", 0)             # 最低价
                        volume = quote_data.get("f47", 0)                # 成交量
                        turnover = quote_data.get("f48", 0)              # 成交额
                        
                        # 计算涨跌幅
                        change_percent = ((current_price - prev_close) / prev_close * 100) if prev_close > 0 else 0
                        
                        return {
                            "stock_code": stock_code,
                            "current_price": round(current_price, 2),
                            "open_price": round(open_price, 2),
                            "high_price": round(high_price, 2),
                            "low_price": round(low_price, 2),
                            "prev_close": round(prev_close, 2),
                            "volume": volume,
                            "turnover": round(turnover, 2),
                            "change_percent": round(change_percent, 2),
                            "timestamp": datetime.utcnow()
                        }
            
            logger.warning(f"未能获取实时行情: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"获取实时行情失败 {stock_code}: {e}")
            return None
    
    async def fetch_kline_data(self, stock_code: str, period: str = "1d", count: int = 100) -> List[Dict[str, Any]]:
        """从东方财富获取K线数据"""
        try:
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                timeout = aiohttp.ClientTimeout(total=30)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                self.session = aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    headers=headers
                )
            
            # 确定市场代码
            market_code = self._get_market_code(stock_code)
            
            # 转换周期参数
            klt_map = {
                "1m": "1", "5m": "5", "15m": "15", "30m": "30", "1h": "60",
                "1d": "101", "1w": "102", "1M": "103"
            }
            klt = klt_map.get(period, "101")
            
            # 东方财富K线数据API
            url = f"{self.kline_url}/api/qt/stock/kline/get"
            params = {
                "secid": f"{market_code}.{stock_code}",
                "klt": klt,
                "fqt": "1",  # 前复权
                "lmt": str(count),
                "end": "20500101",
                "iscca": "1",
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61"
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("rc") == 0 and data.get("data"):
                        klines = data["data"]["klines"]
                        kline_data = []
                        
                        for kline in klines:
                            parts = kline.split(",")
                            if len(parts) >= 11:
                                timestamp = datetime.strptime(parts[0], "%Y-%m-%d")
                                open_price = float(parts[1])
                                close_price = float(parts[2])
                                high_price = float(parts[3])
                                low_price = float(parts[4])
                                volume = int(parts[5])
                                turnover = float(parts[6])
                                
                                kline_data.append({
                                    "stock_code": stock_code,
                                    "period": period,
                                    "timestamp": timestamp,
                                    "open_price": round(open_price, 2),
                                    "high_price": round(high_price, 2),
                                    "low_price": round(low_price, 2),
                                    "close_price": round(close_price, 2),
                                    "volume": volume,
                                    "turnover": round(turnover, 2)
                                })
                        
                        return kline_data
            
            logger.warning(f"未能获取K线数据: {stock_code}")
            return []
            
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
            
            # 创建新的行情记录
            quote = RealtimeQuotes(
                code=stock_code,
                name=stock_name,
                current_price=quote_data["current_price"],
                open_price=quote_data["open_price"],
                high_price=quote_data["high_price"],
                low_price=quote_data["low_price"],
                pre_close=quote_data["prev_close"],
                volume=quote_data["volume"],
                amount=quote_data["turnover"],
                change_amount=quote_data["current_price"] - quote_data["prev_close"],
                change_percent=quote_data["change_percent"],
                quote_time=quote_data["timestamp"]
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
                        KlineData.code == stock_code,
                        KlineData.date == kline_data["timestamp"].date()
                    )
                ).first()
                
                if existing:
                    # 更新现有数据
                    existing.open_price = kline_data["open_price"]
                    existing.high_price = kline_data["high_price"]
                    existing.low_price = kline_data["low_price"]
                    existing.close_price = kline_data["close_price"]
                    existing.volume = kline_data["volume"]
                    existing.amount = kline_data["turnover"]
                else:
                    # 创建新数据
                    open_price = Decimal(str(kline_data["open_price"]))
                    close_price = Decimal(str(kline_data["close_price"]))
                    
                    kline = KlineData(
                        code=stock_code,
                        date=kline_data["timestamp"].date(),
                        open_price=open_price,
                        high_price=kline_data["high_price"],
                        low_price=kline_data["low_price"],
                        close_price=close_price,
                        volume=kline_data["volume"],
                        amount=kline_data["turnover"],
                        change_amount=close_price - open_price,
                        change_percent=((close_price - open_price) / open_price * 100) if open_price > 0 else 0
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
    
    def _get_market_code(self, stock_code: str) -> str:
        """根据股票代码获取市场代码"""
        if stock_code.startswith(("60", "68", "11", "12", "90")):
            return "1"  # 上海交易所
        elif stock_code.startswith(("00", "30", "20")):
            return "0"  # 深圳交易所
        elif stock_code.startswith("8"):
            return "0"  # 北交所（归类为深交所）
        else:
            return "1"  # 默认上海交易所
    
    async def search_stocks_from_api(self, keyword: str, limit: int = 20) -> List[Dict[str, Any]]:
        """从东方财富搜索股票"""
        try:
            if not self.session:
                connector = aiohttp.TCPConnector(ssl=False)
                timeout = aiohttp.ClientTimeout(total=30)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                self.session = aiohttp.ClientSession(
                    connector=connector, 
                    timeout=timeout,
                    headers=headers
                )
            
            url = f"{self.search_url}/api/suggest/get"
            params = {
                "input": keyword,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
                "count": str(limit)
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    stocks = []
                    
                    if data.get("QuotationCodeTable", {}).get("Data"):
                        for item in data["QuotationCodeTable"]["Data"]:
                            stocks.append({
                                "code": item["Code"],
                                "name": item["Name"],
                                "market": item["MktNum"],
                                "type": item["SecurityTypeName"]
                            })
                    
                    return stocks
            
            return []
            
        except Exception as e:
            logger.error(f"搜索股票失败 {keyword}: {e}")
            return []
    
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
    
    def get_user_watchlist_stocks(self, db: Session, user_id: int) -> List[str]:
        """获取用户自选股代码列表"""
        try:
            watchlist = db.query(UserWatchlist).filter(
                UserWatchlist.user_id == user_id
            ).all()
            
            return [item.stock_code for item in watchlist]
            
        except Exception as e:
            logger.error(f"获取用户自选股失败: {e}")
            return []
    
    def get_debug_watchlist_stocks(self, db: Session) -> List[str]:
        """获取调试用的3只自选股"""
        # 为调试固定3只股票
        debug_stocks = ["000001", "600519", "300750"]  # 平安银行、贵州茅台、宁德时代
        
        # 确保这些股票在数据库中存在自选股记录
        for stock_code in debug_stocks:
            existing = db.query(UserWatchlist).filter(
                and_(
                    UserWatchlist.user_id == 1,  # 假设admin用户ID为1
                    UserWatchlist.stock_code == stock_code
                )
            ).first()
            
            if not existing:
                watchlist_item = UserWatchlist(
                    user_id=1,
                    stock_code=stock_code
                )
                db.add(watchlist_item)
        
        try:
            db.commit()
        except Exception as e:
            logger.warning(f"创建调试自选股失败: {e}")
            db.rollback()
        
        return debug_stocks
    
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
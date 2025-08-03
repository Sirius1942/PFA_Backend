#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据采集脚本 - 定期采集东方财富数据到MySQL

使用真实的东方财富API替换模拟数据
"""

import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import List

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal
from app.services.stock_service import stock_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler('logs/data_collection.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollector:
    """数据采集器"""
    
    def __init__(self):
        self.session = SessionLocal
        
    async def collect_watchlist_stocks(self):
        """采集自选股数据（调试用3只股票）"""
        logger.info("开始采集自选股数据...")
        
        # 调试用固定3只股票
        watchlist_stocks = ["000001", "600519", "300750"]  # 平安银行、贵州茅台、宁德时代
        logger.info(f"调试模式：仅采集 {len(watchlist_stocks)} 只自选股")
        
        db = self.session()
        try:
            # 确保调试自选股存在
            debug_stocks = stock_service.get_debug_watchlist_stocks(db)
            
            async with stock_service:
                success_count = 0
                failed_count = 0
                
                for stock_code in watchlist_stocks:
                    try:
                        logger.info(f"采集股票 {stock_code} 数据...")
                        
                        # 采集基本信息
                        await stock_service.update_stock_info(db, stock_code)
                        
                        # 采集实时行情
                        await stock_service.update_realtime_quote(db, stock_code)
                        
                        # 采集K线数据（最近100天）
                        await stock_service.update_kline_data(db, stock_code, "1d", 100)
                        
                        success_count += 1
                        logger.info(f"✅ {stock_code} 数据采集成功")
                        
                        # 避免请求过于频繁
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"❌ {stock_code} 数据采集失败: {e}")
                
                logger.info(f"数据采集完成: 成功 {success_count}, 失败 {failed_count}")
                
        except Exception as e:
            logger.error(f"采集过程中发生错误: {e}")
        finally:
            db.close()
    
    async def collect_realtime_quotes(self, stock_codes: List[str]):
        """批量采集实时行情"""
        logger.info(f"开始批量采集 {len(stock_codes)} 只股票的实时行情...")
        
        db = self.session()
        try:
            async with stock_service:
                results = await stock_service.batch_update_quotes(db, stock_codes)
                
                success_count = sum(1 for success in results.values() if success)
                logger.info(f"实时行情采集完成: 成功 {success_count}/{len(stock_codes)}")
                
        except Exception as e:
            logger.error(f"批量采集实时行情失败: {e}")
        finally:
            db.close()
    
    async def collect_specific_stocks(self, stock_codes: List[str]):
        """采集指定股票的完整数据"""
        logger.info(f"开始采集指定股票数据: {stock_codes}")
        
        db = self.session()
        try:
            async with stock_service:
                for stock_code in stock_codes:
                    try:
                        logger.info(f"采集股票 {stock_code}...")
                        
                        # 采集基本信息
                        await stock_service.update_stock_info(db, stock_code)
                        
                        # 采集实时行情
                        await stock_service.update_realtime_quote(db, stock_code)
                        
                        # 采集日K线（最近252个交易日，约1年）
                        await stock_service.update_kline_data(db, stock_code, "1d", 252)
                        
                        logger.info(f"✅ {stock_code} 完整数据采集成功")
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"❌ {stock_code} 数据采集失败: {e}")
                        
        except Exception as e:
            logger.error(f"采集指定股票数据失败: {e}")
        finally:
            db.close()

async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="股票数据采集脚本")
    parser.add_argument("--mode", choices=["watchlist", "realtime", "custom"], 
                       default="watchlist", help="采集模式")
    parser.add_argument("--codes", nargs="+", help="自定义股票代码列表")
    
    args = parser.parse_args()
    
    collector = DataCollector()
    
    start_time = datetime.now()
    logger.info(f"🚀 数据采集开始 - 模式: {args.mode}")
    
    try:
        if args.mode == "watchlist":
            await collector.collect_watchlist_stocks()
        
        elif args.mode == "realtime":
            if args.codes:
                await collector.collect_realtime_quotes(args.codes)
            else:
                # 默认采集一些热门股票的实时行情
                default_codes = ["600519", "000858", "300750", "002415", "601318"]
                await collector.collect_realtime_quotes(default_codes)
        
        elif args.mode == "custom":
            if not args.codes:
                logger.error("自定义模式需要提供股票代码")
                return
            await collector.collect_specific_stocks(args.codes)
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"🎉 数据采集完成，耗时: {duration:.2f} 秒")
        
    except Exception as e:
        logger.error(f"数据采集失败: {e}")

if __name__ == "__main__":
    asyncio.run(main())
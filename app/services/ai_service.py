from typing import List, Optional, Dict, Any, AsyncGenerator
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import json
import asyncio
from decimal import Decimal

try:
    import openai
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from langchain.memory import ConversationBufferWindowMemory
    from langchain.chains import ConversationChain
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from app.core.config import settings
from app.models.stock import StockInfo, RealtimeQuotes, KlineData
from app.services.stock_service import stock_service
from loguru import logger

class AIAssistantService:
    """AI助手服务类"""
    
    def __init__(self):
        self.openai_api_key = settings.OPENAI_API_KEY
        self.openai_base_url = settings.OPENAI_BASE_URL
        self.model_name = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
        
        # 对话历史存储（实际项目中应该使用数据库或Redis）
        self.conversation_history: Dict[int, List[Dict[str, Any]]] = {}
        
        # 初始化LangChain（如果可用）
        if LANGCHAIN_AVAILABLE and self.openai_api_key:
            try:
                self.llm = ChatOpenAI(
                    model_name=self.model_name,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=self.openai_api_key,
                    openai_api_base=self.openai_base_url
                )
                self.memory = ConversationBufferWindowMemory(
                    k=10,  # 保留最近10轮对话
                    return_messages=True
                )
                self.chain = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    verbose=True
                )
                logger.info("AI助手服务初始化成功")
            except Exception as e:
                logger.error(f"AI助手服务初始化失败: {e}")
                self.llm = None
                self.chain = None
        else:
            self.llm = None
            self.chain = None
            logger.warning("LangChain不可用或OpenAI API密钥未配置，使用模拟模式")
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """
你是一个专业的金融分析师AI助手，专门为用户提供股票投资建议和市场分析。

你的能力包括：
1. 股票基本面分析
2. 技术指标分析
3. 市场趋势判断
4. 投资建议和风险提示
5. 财经新闻解读

请注意：
- 所有投资建议仅供参考，不构成投资决策依据
- 股市有风险，投资需谨慎
- 请根据自身风险承受能力做出投资决策
- 提供的分析要客观、专业、易懂

请用中文回答用户的问题。
"""
    
    async def chat_with_assistant(self, user_id: int, message: str, 
                                 context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """与AI助手对话"""
        try:
            # 获取用户对话历史
            if user_id not in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # 添加用户消息到历史
            user_message = {
                "role": "user",
                "content": message,
                "timestamp": datetime.utcnow(),
                "context": context
            }
            self.conversation_history[user_id].append(user_message)
            
            # 生成AI回复
            if self.chain and LANGCHAIN_AVAILABLE:
                # 使用LangChain生成回复
                response = await self._generate_langchain_response(user_id, message, context)
            else:
                # 使用模拟回复
                response = await self._generate_mock_response(user_id, message, context)
            
            # 添加AI回复到历史
            ai_message = {
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow()
            }
            self.conversation_history[user_id].append(ai_message)
            
            # 限制历史长度
            if len(self.conversation_history[user_id]) > 20:
                self.conversation_history[user_id] = self.conversation_history[user_id][-20:]
            
            return {
                "message": response,
                "timestamp": datetime.utcnow(),
                "context": context
            }
            
        except Exception as e:
            logger.error(f"AI对话失败: {e}")
            return {
                "message": "抱歉，我现在无法回答您的问题，请稍后再试。",
                "timestamp": datetime.utcnow(),
                "error": str(e)
            }
    
    async def _generate_langchain_response(self, user_id: int, message: str, 
                                         context: Optional[Dict[str, Any]] = None) -> str:
        """使用LangChain生成回复"""
        try:
            # 构建完整的提示
            full_prompt = self._build_prompt_with_context(message, context)
            
            # 生成回复
            def _call_chain():
                return self.chain.predict(input=full_prompt)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, _call_chain
            )
            
            return response
            
        except Exception as e:
            logger.error(f"LangChain生成回复失败: {e}")
            return await self._generate_mock_response(user_id, message, context)
    
    async def _generate_mock_response(self, user_id: int, message: str, 
                                    context: Optional[Dict[str, Any]] = None) -> str:
        """生成模拟回复"""
        # 简单的关键词匹配回复
        message_lower = message.lower()
        
        if any(keyword in message_lower for keyword in ["股票", "股价", "行情"]):
            return "我可以帮您分析股票行情。请提供具体的股票代码，我会为您提供详细的技术分析和投资建议。请注意，所有建议仅供参考，投资有风险。"
        
        elif any(keyword in message_lower for keyword in ["买入", "卖出", "投资"]):
            return "投资决策需要综合考虑多个因素，包括基本面、技术面、市场环境等。建议您：\n1. 充分了解公司基本面\n2. 分析技术指标\n3. 考虑市场整体趋势\n4. 评估自身风险承受能力\n\n请记住，股市有风险，投资需谨慎。"
        
        elif any(keyword in message_lower for keyword in ["风险", "亏损"]):
            return "投资风险管理非常重要：\n1. 分散投资，不要把鸡蛋放在一个篮子里\n2. 设置止损点\n3. 控制仓位大小\n4. 定期评估投资组合\n5. 保持理性，避免情绪化交易\n\n如需具体的风险评估，请提供您的投资组合信息。"
        
        elif any(keyword in message_lower for keyword in ["市场", "趋势", "走势"]):
            return "当前市场分析：\n1. 整体趋势：需要关注宏观经济指标\n2. 行业轮动：科技、消费、金融等板块表现\n3. 资金流向：关注北向资金和机构动向\n4. 政策影响：货币政策和产业政策\n\n建议保持谨慎乐观的态度，做好风险控制。"
        
        else:
            return "您好！我是您的专业金融分析师助手。我可以帮您：\n\n📈 股票分析和投资建议\n📊 市场趋势分析\n💰 投资组合优化\n⚠️ 风险评估和管理\n📰 财经新闻解读\n\n请告诉我您想了解什么，我会为您提供专业的分析和建议。"
    
    def _build_prompt_with_context(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """构建包含上下文的提示"""
        prompt_parts = [self._get_system_prompt()]
        
        if context:
            if "stock_data" in context:
                stock_data = context["stock_data"]
                prompt_parts.append(f"\n当前股票信息：{json.dumps(stock_data, ensure_ascii=False, indent=2)}")
            
            if "market_data" in context:
                market_data = context["market_data"]
                prompt_parts.append(f"\n市场数据：{json.dumps(market_data, ensure_ascii=False, indent=2)}")
        
        prompt_parts.append(f"\n用户问题：{message}")
        
        return "\n".join(prompt_parts)
    
    async def analyze_stock(self, db: Session, stock_code: str, 
                          analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """AI股票分析"""
        try:
            # 获取股票基本信息
            stock_info = db.query(StockInfo).filter(StockInfo.code == stock_code).first()
            if not stock_info:
                return {"error": "股票不存在"}
            
            # 获取实时行情
            latest_quote = db.query(RealtimeQuotes).filter(
                RealtimeQuotes.stock_code == stock_code
            ).order_by(RealtimeQuotes.timestamp.desc()).first()
            
            # 获取K线数据（最近30天）
            kline_data = db.query(KlineData).filter(
                KlineData.stock_code == stock_code
            ).order_by(KlineData.timestamp.desc()).limit(30).all()
            
            # 构建分析上下文
            context = {
                "stock_info": {
                    "code": stock_info.code,
                    "name": stock_info.name,
                    "market": stock_info.market,
                    "industry": stock_info.industry,
                    "sector": stock_info.sector
                },
                "latest_quote": {
                    "current_price": float(latest_quote.current_price) if latest_quote else None,
                    "change_percent": float(latest_quote.change_percent) if latest_quote else None,
                    "volume": latest_quote.volume if latest_quote else None
                } if latest_quote else None,
                "kline_summary": {
                    "period_count": len(kline_data),
                    "price_trend": self._analyze_price_trend(kline_data),
                    "volume_trend": self._analyze_volume_trend(kline_data)
                } if kline_data else None
            }
            
            # 生成分析报告
            analysis_prompt = f"请对股票 {stock_info.name}({stock_code}) 进行{analysis_type}分析"
            
            if self.chain and LANGCHAIN_AVAILABLE:
                analysis = await self._generate_langchain_response(0, analysis_prompt, {"stock_data": context})
            else:
                analysis = await self._generate_stock_analysis_mock(stock_info, latest_quote, kline_data, analysis_type)
            
            return {
                "stock_code": stock_code,
                "stock_name": stock_info.name,
                "analysis_type": analysis_type,
                "analysis": analysis,
                "context": context,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"股票分析失败 {stock_code}: {e}")
            return {"error": f"分析失败: {str(e)}"}
    
    async def _generate_stock_analysis_mock(self, stock_info: StockInfo, 
                                          latest_quote: Optional[RealtimeQuotes],
                                          kline_data: List[KlineData],
                                          analysis_type: str) -> str:
        """生成模拟股票分析"""
        analysis_parts = []
        
        # 基本信息
        analysis_parts.append(f"## {stock_info.name}({stock_info.code}) 分析报告")
        analysis_parts.append(f"**所属行业**: {stock_info.industry or '未知'}")
        analysis_parts.append(f"**所属板块**: {stock_info.sector or '未知'}")
        analysis_parts.append(f"**交易市场**: {stock_info.market}")
        
        # 当前行情
        if latest_quote:
            analysis_parts.append("\n### 当前行情")
            analysis_parts.append(f"- 当前价格: ¥{latest_quote.current_price}")
            analysis_parts.append(f"- 涨跌幅: {latest_quote.change_percent:+.2f}%")
            analysis_parts.append(f"- 成交量: {latest_quote.volume:,}")
            
            # 简单的技术分析
            if latest_quote.change_percent > 5:
                analysis_parts.append("- 技术信号: 强势上涨，注意回调风险")
            elif latest_quote.change_percent > 2:
                analysis_parts.append("- 技术信号: 温和上涨，可关注")
            elif latest_quote.change_percent < -5:
                analysis_parts.append("- 技术信号: 大幅下跌，可能存在机会")
            elif latest_quote.change_percent < -2:
                analysis_parts.append("- 技术信号: 调整中，观望为主")
            else:
                analysis_parts.append("- 技术信号: 震荡整理，等待方向")
        
        # 趋势分析
        if kline_data:
            analysis_parts.append("\n### 趋势分析")
            trend = self._analyze_price_trend(kline_data)
            analysis_parts.append(f"- 价格趋势: {trend}")
            
            volume_trend = self._analyze_volume_trend(kline_data)
            analysis_parts.append(f"- 成交量趋势: {volume_trend}")
        
        # 投资建议
        analysis_parts.append("\n### 投资建议")
        if latest_quote and latest_quote.change_percent > 0:
            analysis_parts.append("- 短期: 谨慎乐观，注意风险控制")
            analysis_parts.append("- 中期: 关注基本面变化")
        else:
            analysis_parts.append("- 短期: 观望为主，等待企稳信号")
            analysis_parts.append("- 中期: 可适当关注，分批建仓")
        
        # 风险提示
        analysis_parts.append("\n### 风险提示")
        analysis_parts.append("- 本分析仅供参考，不构成投资建议")
        analysis_parts.append("- 股市有风险，投资需谨慎")
        analysis_parts.append("- 请根据自身风险承受能力做出投资决策")
        
        return "\n".join(analysis_parts)
    
    def _analyze_price_trend(self, kline_data: List[KlineData]) -> str:
        """分析价格趋势"""
        if not kline_data or len(kline_data) < 2:
            return "数据不足"
        
        # 按时间排序
        sorted_data = sorted(kline_data, key=lambda x: x.timestamp)
        
        # 计算价格变化
        start_price = float(sorted_data[0].close_price)
        end_price = float(sorted_data[-1].close_price)
        change_percent = (end_price - start_price) / start_price * 100
        
        if change_percent > 10:
            return "强势上涨"
        elif change_percent > 5:
            return "温和上涨"
        elif change_percent > -5:
            return "震荡整理"
        elif change_percent > -10:
            return "温和下跌"
        else:
            return "大幅下跌"
    
    def _analyze_volume_trend(self, kline_data: List[KlineData]) -> str:
        """分析成交量趋势"""
        if not kline_data or len(kline_data) < 5:
            return "数据不足"
        
        # 按时间排序
        sorted_data = sorted(kline_data, key=lambda x: x.timestamp)
        
        # 计算平均成交量
        recent_volume = sum(item.volume for item in sorted_data[-5:]) / 5
        earlier_volume = sum(item.volume for item in sorted_data[-10:-5]) / 5 if len(sorted_data) >= 10 else recent_volume
        
        if recent_volume > earlier_volume * 1.5:
            return "放量"
        elif recent_volume < earlier_volume * 0.7:
            return "缩量"
        else:
            return "平稳"
    
    async def get_market_insights(self, db: Session) -> Dict[str, Any]:
        """获取市场洞察"""
        try:
            # 获取市场统计数据
            market_stats = stock_service.get_market_summary(db)
            
            # 生成市场洞察
            insights_prompt = "请基于当前市场数据提供市场洞察和投资建议"
            
            if self.chain and LANGCHAIN_AVAILABLE:
                insights = await self._generate_langchain_response(0, insights_prompt, {"market_data": market_stats})
            else:
                insights = await self._generate_market_insights_mock(market_stats)
            
            return {
                "insights": insights,
                "market_stats": market_stats,
                "timestamp": datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"获取市场洞察失败: {e}")
            return {"error": f"获取失败: {str(e)}"}
    
    async def _generate_market_insights_mock(self, market_stats: Dict[str, Any]) -> str:
        """生成模拟市场洞察"""
        insights = []
        
        insights.append("## 市场洞察报告")
        insights.append(f"**报告时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        if market_stats:
            total_stocks = market_stats.get("total_stocks", 0)
            insights.append(f"\n### 市场概况")
            insights.append(f"- 总股票数量: {total_stocks}")
            
            market_dist = market_stats.get("market_distribution", {})
            for market, count in market_dist.items():
                insights.append(f"- {market}市场: {count}只股票")
        
        insights.append("\n### 投资策略建议")
        insights.append("1. **分散投资**: 不要将资金集中在单一股票或行业")
        insights.append("2. **价值投资**: 关注基本面良好的优质公司")
        insights.append("3. **风险控制**: 设置合理的止损点")
        insights.append("4. **长期持有**: 避免频繁交易")
        
        insights.append("\n### 市场风险提示")
        insights.append("- 当前市场波动较大，建议谨慎操作")
        insights.append("- 关注宏观经济政策变化")
        insights.append("- 注意国际市场影响")
        
        return "\n".join(insights)
    
    def get_conversation_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取对话历史"""
        if user_id not in self.conversation_history:
            return []
        
        history = self.conversation_history[user_id]
        return history[-limit:] if limit > 0 else history
    
    def clear_conversation_history(self, user_id: int) -> bool:
        """清空对话历史"""
        try:
            if user_id in self.conversation_history:
                self.conversation_history[user_id] = []
            
            # 重置LangChain内存
            if self.memory:
                self.memory.clear()
            
            return True
            
        except Exception as e:
            logger.error(f"清空对话历史失败: {e}")
            return False
    
    async def get_smart_suggestions(self, db: Session, user_id: int, 
                                  suggestion_type: str = "general") -> List[Dict[str, Any]]:
        """获取智能建议"""
        try:
            suggestions = []
            
            if suggestion_type == "watchlist":
                # 基于用户自选股的建议
                suggestions = await self._get_watchlist_suggestions(db, user_id)
            elif suggestion_type == "market":
                # 市场机会建议
                suggestions = await self._get_market_suggestions(db)
            else:
                # 通用建议
                suggestions = await self._get_general_suggestions()
            
            return suggestions
            
        except Exception as e:
            logger.error(f"获取智能建议失败: {e}")
            return []
    
    async def _get_watchlist_suggestions(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """获取自选股相关建议"""
        # 这里应该基于用户的自选股进行分析
        return [
            {
                "type": "watchlist",
                "title": "关注自选股动态",
                "content": "建议定期检查自选股的基本面变化和技术指标",
                "priority": "medium",
                "timestamp": datetime.utcnow()
            }
        ]
    
    async def _get_market_suggestions(self, db: Session) -> List[Dict[str, Any]]:
        """获取市场机会建议"""
        return [
            {
                "type": "market",
                "title": "关注行业轮动",
                "content": "当前科技板块表现活跃，建议关注相关优质标的",
                "priority": "high",
                "timestamp": datetime.utcnow()
            }
        ]
    
    async def _get_general_suggestions(self) -> List[Dict[str, Any]]:
        """获取通用建议"""
        return [
            {
                "type": "general",
                "title": "风险管理",
                "content": "建议设置合理的止损点，控制单笔投资金额",
                "priority": "high",
                "timestamp": datetime.utcnow()
            },
            {
                "type": "general",
                "title": "学习提升",
                "content": "建议定期学习投资知识，提升分析能力",
                "priority": "medium",
                "timestamp": datetime.utcnow()
            }
        ]

# 创建全局服务实例
ai_service = AIAssistantService()
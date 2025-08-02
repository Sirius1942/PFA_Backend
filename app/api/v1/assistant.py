from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json
import asyncio

from app.core.database import get_db
from app.models.user import User
from app.core.deps import get_current_user
from app.auth.permissions import require_permission, Permissions
from app.services.ai_service import ai_service
from pydantic import BaseModel

router = APIRouter(tags=["AI助手"])

# Pydantic模型
class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: Optional[datetime] = None

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None
    stock_code: Optional[str] = None
    analysis_type: Optional[str] = None  # technical, fundamental, sentiment

class ChatResponse(BaseModel):
    message: str
    suggestions: Optional[List[str]] = None
    charts: Optional[List[Dict[str, Any]]] = None
    analysis_data: Optional[Dict[str, Any]] = None
    timestamp: datetime

class StockAnalysisRequest(BaseModel):
    stock_code: str
    analysis_type: str  # technical, fundamental, comprehensive
    period: Optional[str] = "1d"  # K线周期
    days: Optional[int] = 30  # 分析天数

class StockAnalysisResponse(BaseModel):
    stock_code: str
    stock_name: str
    analysis_type: str
    summary: str
    detailed_analysis: Dict[str, Any]
    recommendations: List[str]
    risk_assessment: Dict[str, Any]
    charts: Optional[List[Dict[str, Any]]] = None
    timestamp: datetime

class MarketInsightRequest(BaseModel):
    market: Optional[str] = None  # SH, SZ, BJ
    industry: Optional[str] = None
    insight_type: str = "overview"  # overview, trend, hotspots

class MarketInsightResponse(BaseModel):
    insight_type: str
    title: str
    summary: str
    key_points: List[str]
    market_data: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

# 注意：现在使用真实的AI服务而不是模拟实现
# AI服务实例已通过导入获得: from app.services.ai_service import ai_service

@router.post("/chat", response_model=ChatResponse)
@require_permission(Permissions.USE_AI_ASSISTANT)
async def chat_with_assistant(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """与AI助手对话"""
    try:
        response = await ai_service.chat_with_assistant(
            user_id=current_user.id,
            message=request.message,
            context=request.context
        )
        
        # 转换为API响应格式
        return ChatResponse(
            message=response["message"],
            suggestions=response.get("suggestions"),
            charts=response.get("charts"),
            analysis_data=response.get("analysis_data"),
            timestamp=response.get("timestamp", datetime.utcnow())
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI服务暂时不可用: {str(e)}"
        )

@router.post("/analyze-stock", response_model=StockAnalysisResponse)
@require_permission(Permissions.USE_AI_ASSISTANT)
async def analyze_stock(
    request: StockAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """AI股票分析"""
    try:
        analysis = await ai_service.analyze_stock(
            db=db,
            stock_code=request.stock_code,
            analysis_type=request.analysis_type
        )
        
        # 转换为API响应格式
        return StockAnalysisResponse(
            stock_code=analysis["stock_code"],
            stock_name=analysis["stock_name"],
            analysis_type=analysis["analysis_type"],
            summary=analysis["analysis"],
            detailed_analysis=analysis.get("context", {}),
            recommendations=[],
            risk_assessment={},
            charts=None,
            timestamp=analysis.get("timestamp", datetime.utcnow())
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"股票分析服务暂时不可用: {str(e)}"
        )

@router.post("/market-insights", response_model=MarketInsightResponse)
@require_permission(Permissions.USE_AI_ASSISTANT)
async def get_market_insights(
    request: MarketInsightRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取市场洞察"""
    try:
        insights = await ai_service.get_market_insights(db=db)
        
        # 转换为API响应格式
        return MarketInsightResponse(
            insight_type=request.insight_type,
            title="市场洞察",
            summary=insights["insights"],
            key_points=["基于AI分析的市场洞察"],
            market_data=insights.get("market_stats", {}),
            recommendations=["请谨慎投资", "注意风险控制"],
            timestamp=insights.get("timestamp", datetime.utcnow())
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"市场洞察服务暂时不可用: {str(e)}"
        )

@router.get("/conversation-history")
@require_permission(Permissions.USE_AI_ASSISTANT)
async def get_conversation_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """获取对话历史"""
    return ai_service.get_conversation_history(current_user.id, limit)

@router.delete("/conversation-history")
@require_permission(Permissions.USE_AI_ASSISTANT)
async def clear_conversation_history(
    current_user: User = Depends(get_current_user)
):
    """清空对话历史"""
    success = ai_service.clear_conversation_history(current_user.id)
    return {"message": "对话历史已清空" if success else "清空失败"}

@router.get("/suggestions")
@require_permission(Permissions.USE_AI_ASSISTANT)
async def get_suggestions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取智能建议"""
    suggestion_type = "general"
    return await ai_service.get_smart_suggestions(db, current_user.id, suggestion_type)
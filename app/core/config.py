#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理
"""

import os
import json
from typing import List, Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache

def load_config_json() -> Dict[str, Any]:
    """从config.json加载配置"""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用基础配置
    APP_NAME: str = "私人金融分析师"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str
    DATABASE_ECHO: bool = False
    
    # Redis配置
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS配置
    ALLOWED_HOSTS: List[str] = ["*"]
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    # 外部API配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # 东方财富API配置
    EASTMONEY_API_BASE: str = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # 缓存配置
    CACHE_EXPIRE_SECONDS: int = 300  # 5分钟
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    def __init__(self, **kwargs):
        # 首先从config.json加载配置
        config_json = load_config_json()
        
        # 从JSON配置中提取相关值
        if config_json:
            # 数据库配置
            if "database" in config_json:
                kwargs.setdefault("DATABASE_URL", config_json["database"].get("url", "mysql+pymysql://financial_user:financial123@localhost:3307/financial_db"))
                kwargs.setdefault("DATABASE_ECHO", config_json["database"].get("echo", False))
            
            # OpenAI配置
            if "openai" in config_json:
                openai_config = config_json["openai"]
                kwargs.setdefault("OPENAI_API_KEY", openai_config.get("api_key"))
                kwargs.setdefault("OPENAI_BASE_URL", openai_config.get("base_url"))
                kwargs.setdefault("OPENAI_MODEL", openai_config.get("model", "gpt-3.5-turbo"))
                kwargs.setdefault("OPENAI_TEMPERATURE", openai_config.get("temperature", 0.7))
                kwargs.setdefault("OPENAI_MAX_TOKENS", openai_config.get("max_tokens", 2000))
            
            # 日志配置
            if "logging" in config_json:
                logging_config = config_json["logging"]
                kwargs.setdefault("LOG_LEVEL", logging_config.get("level", "INFO"))
                kwargs.setdefault("LOG_FILE", logging_config.get("file", "logs/app.log"))
        
        # 没有从config.json获取到数据库URL时使用默认值
        kwargs.setdefault("DATABASE_URL", "mysql+pymysql://financial_user:financial123@localhost:3307/financial_db")
        
        super().__init__(**kwargs)
    
    @field_validator("ALLOWED_HOSTS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [host.strip() for host in v.split(",")]
        return v
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True
    }

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例模式）"""
    return Settings()

# 全局配置实例
settings = get_settings()
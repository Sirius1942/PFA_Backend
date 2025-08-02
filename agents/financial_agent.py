#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
金融量化分析师Agent

基于LangChain构建的智能金融分析助手，集成股票数据查询、技术分析、
市场研究和多轮对话记忆功能。

功能特性：
1. 股票信息查询和搜索
2. 实时行情和历史数据分析
3. 技术指标计算和趋势分析
4. 市场概览和排行榜
5. 网络搜索获取最新财经资讯
6. 多轮对话记忆
7. 文件操作和数据导出

作者: Assistant
日期: 2024
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# LangChain imports - 使用最新版本的导入
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
# Shell工具（实验性功能）
try:
    from langchain_experimental.tools import ShellTool
except ImportError:
    ShellTool = None
    print("⚠️ Shell工具不可用，需要安装 langchain-experimental")
# 文件管理工具
from langchain_community.tools.file_management import (
    ReadFileTool,
    WriteFileTool,
    ListDirectoryTool,
)

# Tavily search
from langchain_tavily import TavilySearch

# 导入数据库工具
from tools.database_tools import StockDatabaseTools
from tools.data_calculator import DataCalculator

class FinancialQuantAgent:
    """
    金融量化分析师Agent
    """
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        初始化金融分析Agent
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self.load_config(config_path)
        self.db_tools = StockDatabaseTools(self.config['database']['path'])
        
        # 初始化数据计算器
        self.data_calculator = DataCalculator(db_path=self.config['database']['path'])
        
        self.agent = None
        self.memory = None
        self._setup_agent()
    
    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            配置字典
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 设置环境变量
            if 'openai_api_key' in config:
                os.environ['OPENAI_API_KEY'] = config['openai_api_key']
            if 'tavily_api_key' in config:
                os.environ['TAVILY_API_KEY'] = config['tavily_api_key']
            
            return config
            
        except Exception as e:
            print(f"❌ 加载配置文件失败: {e}")
            return {}
    
    def _setup_agent(self):
        """
        设置Agent和工具
        """
        # 初始化LLM
        llm = ChatOpenAI(
            api_key=self.config['openai']['api_key'],
            base_url=self.config['openai']['base_url'],
            model=self.config['openai']['model'],
            temperature=self.config['openai']['temperature'],
            max_tokens=self.config['openai']['max_tokens']
        )
        
        # 初始化记忆
        # 注意：ConversationBufferWindowMemory 已被弃用，建议迁移到 LangGraph 持久化
        # 详见：https://python.langchain.com/docs/versions/migrating_memory/
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10  # 保留最近10轮对话
        )
        
        # 创建工具列表
        tools = self._create_tools()
        
        # 创建系统提示
        system_prompt = self._create_system_prompt()
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # 创建Agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        
        # 创建Agent执行器
        self.agent = AgentExecutor(
            agent=agent,
            tools=tools,
            memory=self.memory,
            verbose=True,
            max_iterations=5,
            early_stopping_method="generate"
        )
    
    def _create_tools(self) -> List[Tool]:
        """
        创建工具列表
        
        Returns:
            工具列表
        """
        tools = []
        
        # 股票信息查询工具
        tools.append(Tool(
            name="stock_info_query",
            description="查询股票基本信息。输入股票代码或名称，返回股票的基本信息如市值、行业等。",
            func=self._stock_info_wrapper
        ))
        
        # 实时行情查询工具
        tools.append(Tool(
            name="realtime_quotes",
            description="查询股票实时行情数据。输入股票代码，返回最新的价格、涨跌幅、成交量等信息。",
            func=self._realtime_quotes_wrapper
        ))
        
        # 历史数据查询工具
        tools.append(Tool(
            name="historical_data",
            description="查询股票历史K线数据。输入格式：股票代码,开始日期,结束日期,数量限制。日期格式：YYYY-MM-DD。",
            func=self._historical_data_wrapper
        ))
        
        # 股票搜索工具
        tools.append(Tool(
            name="stock_search",
            description="搜索股票。输入关键词（股票代码或名称），返回匹配的股票列表及其最新行情。",
            func=self._stock_search_wrapper
        ))
        
        # 市场概览工具
        tools.append(Tool(
            name="market_overview",
            description="获取市场概览统计信息，包括涨跌统计、成交量统计、市场分布等。",
            func=self._market_overview_wrapper
        ))
        
        # 排行榜工具
        tools.append(Tool(
            name="top_performers",
            description="获取股票排行榜。输入格式：指标,数量,排序方式。指标可选：change_percent(涨跌幅)、volume(成交量)、turnover(成交额)、market_cap(市值)。排序方式：desc(降序)或asc(升序)。",
            func=self._top_performers_wrapper
        ))
        
        # 股票分析工具
        tools.append(Tool(
            name="stock_analysis",
            description="对指定股票进行综合分析，包括基本信息、最新行情、历史数据和技术指标分析。",
            func=self._stock_analysis_wrapper
        ))
        
        # 数据计算工具
        tools.append(Tool(
            name="data_calculation",
            description="使用pandas进行数据计算，如修复涨跌幅计算、计算技术指标等。输入格式：股票代码,计算类型。计算类型可选：price_change(修复涨跌幅)、technical_indicators(技术指标)。",
            func=self._data_calculation_wrapper
        ))
        
        # 网络搜索工具
        try:
            # 设置环境变量
            os.environ['TAVILY_API_KEY'] = self.config['tavily']['api_key']
            tavily_search = TavilySearch(
                max_results=5
            )
            tools.append(Tool(
                name="web_search",
                description="搜索最新的财经新闻和市场资讯。用于获取实时的市场动态、公司公告、行业分析等信息。",
                func=tavily_search.run
            ))
        except Exception as e:
            print(f"⚠️ Tavily搜索工具初始化失败: {e}")
        
        # 文件操作工具
        tools.extend([
            ReadFileTool(),
            WriteFileTool(),
            ListDirectoryTool(),
        ])
        
        # Shell工具（谨慎使用）
        if ShellTool is not None:
            try:
                shell_tool = ShellTool()
                shell_tool.description = "执行系统命令。请谨慎使用，主要用于文件操作、数据处理等安全操作。"
                tools.append(shell_tool)
            except Exception as e:
                print(f"⚠️ Shell工具初始化失败: {e}")
        else:
            print("⚠️ Shell工具不可用，需要安装 langchain-experimental")
        
        return tools
    
    def _create_system_prompt(self) -> str:
        """
        创建系统提示
        
        Returns:
            系统提示字符串
        """
        return """
你是一位专业的金融量化分析师AI助手，具备以下核心能力：

🎯 **专业领域**：
- 股票市场分析和投资建议
- 技术指标分析和趋势判断
- 市场数据查询和统计分析
- 财经资讯搜索和解读
- 量化策略建议

🛠️ **可用工具**：
1. **股票数据查询**：股票信息、实时行情、历史数据
2. **市场分析**：市场概览、排行榜、综合分析
3. **数据计算**：使用pandas进行精确的数据计算和修复
4. **信息搜索**：最新财经新闻和市场资讯
5. **文件操作**：数据导出、报告生成
6. **系统命令**：数据处理和分析

🧮 **数据计算能力**：
- 使用pandas进行精确的数据计算
- 修复涨跌幅等指标的计算错误
- 自动创建临时脚本进行复杂计算
- 计算完成后自动清理临时文件
- 支持技术指标的精确计算

📋 **工作原则**：
1. **数据驱动**：基于真实数据进行分析，避免主观臆测
2. **风险提示**：投资建议必须包含风险警示
3. **专业术语**：使用准确的金融术语，但要通俗易懂
4. **及时性**：关注市场动态，提供最新信息
5. **客观中立**：保持客观立场，不做过度乐观或悲观的判断
6. **数据准确性**：发现数据计算错误时，自动使用data_calculation工具修复

💡 **交互方式**：
- 主动询问用户需求的具体细节
- 提供清晰的数据分析和图表说明
- 给出可操作的投资建议和风险控制措施
- 记住用户的投资偏好和历史咨询内容
- 发现数据异常时主动使用计算工具验证和修复

⚠️ **重要声明**：
所有分析和建议仅供参考，不构成投资建议。投资有风险，入市需谨慎。

现在，我准备为您提供专业的金融分析服务。请告诉我您需要什么帮助？
"""
    
    def _stock_info_wrapper(self, query: str) -> str:
        """
        股票信息查询包装器
        """
        try:
            # 解析查询参数
            if query.isdigit() or '.' in query:
                # 股票代码查询
                results = self.db_tools.get_stock_info(code=query)
            else:
                # 股票名称查询
                results = self.db_tools.get_stock_info(name=query)
            
            if not results:
                return f"未找到股票信息：{query}"
            
            # 格式化输出
            output = []
            for stock in results[:5]:  # 限制显示前5个结果
                info = (
                    f"代码：{stock.get('code', 'N/A')}\n"
                    f"名称：{stock.get('name', 'N/A')}\n"
                    f"市场：{stock.get('market', 'N/A')}\n"
                    f"行业：{stock.get('industry', 'N/A')}\n"
                    f"市值：{stock.get('market_cap', 'N/A')}\n"
                    f"上市日期：{stock.get('list_date', 'N/A')}\n"
                )
                output.append(info)
            
            return "\n" + "="*50 + "\n".join(output)
            
        except Exception as e:
            return f"查询股票信息时出错：{str(e)}"
    
    def _realtime_quotes_wrapper(self, query: str) -> str:
        """
        实时行情查询包装器
        """
        try:
            code = query.strip()
            results = self.db_tools.get_realtime_quotes(code=code, limit=1)
            
            if not results:
                return f"未找到股票 {code} 的实时行情数据"
            
            quote = results[0]
            output = (
                f"📈 {code} 实时行情\n"
                f"当前价：{quote.get('current_price', 'N/A')}\n"
                f"涨跌额：{quote.get('change_amount', 'N/A')}\n"
                f"涨跌幅：{quote.get('change_percent', 'N/A')}%\n"
                f"开盘价：{quote.get('open_price', 'N/A')}\n"
                f"最高价：{quote.get('high_price', 'N/A')}\n"
                f"最低价：{quote.get('low_price', 'N/A')}\n"
                f"成交量：{quote.get('volume', 'N/A')}\n"
                f"成交额：{quote.get('turnover', 'N/A')}\n"
                f"更新时间：{quote.get('timestamp', 'N/A')}"
            )
            
            return output
            
        except Exception as e:
            return f"查询实时行情时出错：{str(e)}"
    
    def _historical_data_wrapper(self, query: str) -> str:
        """
        历史数据查询包装器
        """
        try:
            # 解析参数：股票代码,开始日期,结束日期,数量限制
            params = [p.strip() for p in query.split(',')]
            code = params[0]
            start_date = params[1] if len(params) > 1 else None
            end_date = params[2] if len(params) > 2 else None
            limit = int(params[3]) if len(params) > 3 and params[3].isdigit() else 10
            
            results = self.db_tools.get_kline_data(code, start_date, end_date, limit)
            
            if not results:
                return f"未找到股票 {code} 的历史数据"
            
            output = [f"📊 {code} 历史K线数据（最近{len(results)}条）\n"]
            output.append("日期\t\t开盘\t最高\t最低\t收盘\t成交量")
            output.append("-" * 60)
            
            for data in results[:10]:  # 限制显示条数
                line = (
                    f"{data.get('date', 'N/A')}\t"
                    f"{data.get('open_price', 'N/A')}\t"
                    f"{data.get('high_price', 'N/A')}\t"
                    f"{data.get('low_price', 'N/A')}\t"
                    f"{data.get('close_price', 'N/A')}\t"
                    f"{data.get('volume', 'N/A')}"
                )
                output.append(line)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"查询历史数据时出错：{str(e)}"
    
    def _stock_search_wrapper(self, query: str) -> str:
        """
        股票搜索包装器
        """
        try:
            results = self.db_tools.search_stocks(query, limit=10)
            
            if not results:
                return f"未找到匹配 '{query}' 的股票"
            
            output = [f"🔍 搜索结果：'{query}'（共{len(results)}条）\n"]
            output.append("代码\t\t名称\t\t\t当前价\t涨跌幅")
            output.append("-" * 50)
            
            for stock in results:
                line = (
                    f"{stock.get('code', 'N/A')}\t"
                    f"{stock.get('name', 'N/A')[:8]}\t\t"
                    f"{stock.get('current_price', 'N/A')}\t"
                    f"{stock.get('change_percent', 'N/A')}%"
                )
                output.append(line)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"搜索股票时出错：{str(e)}"
    
    def _market_overview_wrapper(self, query: str = "") -> str:
        """
        市场概览包装器
        """
        try:
            overview = self.db_tools.get_market_overview()
            
            if not overview:
                return "暂无市场概览数据"
            
            output = ["📊 市场概览\n"]
            
            # 价格统计
            if 'price_statistics' in overview:
                stats = overview['price_statistics']
                output.extend([
                    "📈 涨跌统计：",
                    f"  上涨股票：{stats.get('rising_count', 0)} 只",
                    f"  下跌股票：{stats.get('falling_count', 0)} 只",
                    f"  平盘股票：{stats.get('flat_count', 0)} 只",
                    f"  平均涨跌幅：{stats.get('avg_change_percent', 0):.2f}%",
                    f"  最大涨幅：{stats.get('max_change_percent', 0):.2f}%",
                    f"  最大跌幅：{stats.get('min_change_percent', 0):.2f}%\n"
                ])
            
            # 成交量统计
            if 'volume_statistics' in overview:
                vol_stats = overview['volume_statistics']
                output.extend([
                    "💰 成交统计：",
                    f"  总成交量：{vol_stats.get('total_volume', 0)}",
                    f"  总成交额：{vol_stats.get('total_turnover', 0)}",
                    f"  平均成交量：{vol_stats.get('avg_volume', 0):.0f}",
                    f"  平均成交额：{vol_stats.get('avg_turnover', 0):.0f}\n"
                ])
            
            # 市场分布
            if 'market_distribution' in overview:
                output.append("🏢 市场分布：")
                for market in overview['market_distribution']:
                    output.append(f"  {market.get('market', 'N/A')}：{market.get('count', 0)} 只")
            
            output.append(f"\n⏰ 更新时间：{overview.get('update_time', 'N/A')}")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"获取市场概览时出错：{str(e)}"
    
    def _top_performers_wrapper(self, query: str) -> str:
        """
        排行榜包装器
        """
        try:
            # 解析参数：指标,数量,排序方式
            params = [p.strip() for p in query.split(',')]
            metric = params[0] if len(params) > 0 else "change_percent"
            limit = int(params[1]) if len(params) > 1 and params[1].isdigit() else 10
            order = params[2].lower() if len(params) > 2 else "desc"
            
            ascending = order == "asc"
            results = self.db_tools.get_top_performers(metric, limit, ascending)
            
            if not results:
                return f"未找到 {metric} 排行榜数据"
            
            # 指标名称映射
            metric_names = {
                'change_percent': '涨跌幅',
                'volume': '成交量',
                'turnover': '成交额',
                'market_cap': '市值'
            }
            
            metric_name = metric_names.get(metric, metric)
            order_name = "升序" if ascending else "降序"
            
            output = [f"🏆 {metric_name}排行榜（{order_name}，前{len(results)}名）\n"]
            output.append("排名\t代码\t\t名称\t\t\t指标值")
            output.append("-" * 50)
            
            for i, stock in enumerate(results, 1):
                value = stock.get(metric, 'N/A')
                if metric == 'change_percent':
                    value = f"{value}%" if value != 'N/A' else 'N/A'
                
                line = (
                    f"{i}\t"
                    f"{stock.get('code', 'N/A')}\t"
                    f"{stock.get('name', 'N/A')[:8]}\t\t"
                    f"{value}"
                )
                output.append(line)
            
            return "\n".join(output)
            
        except Exception as e:
            return f"获取排行榜时出错：{str(e)}"
    
    def _stock_analysis_wrapper(self, query: str) -> str:
        """
        股票分析包装器
        """
        try:
            code = query.strip()
            analysis = self.db_tools.get_stock_analysis(code)
            
            if 'error' in analysis:
                return f"分析失败：{analysis['error']}"
            
            output = [f"📊 {code} 综合分析报告\n"]
            
            # 基本信息
            if 'basic_info' in analysis:
                info = analysis['basic_info']
                output.extend([
                    "📋 基本信息：",
                    f"  股票名称：{info.get('name', 'N/A')}",
                    f"  所属市场：{info.get('market', 'N/A')}",
                    f"  所属行业：{info.get('industry', 'N/A')}",
                    f"  市值：{info.get('market_cap', 'N/A')}",
                    f"  上市日期：{info.get('list_date', 'N/A')}\n"
                ])
            
            # 最新行情
            if 'latest_quote' in analysis and analysis['latest_quote']:
                quote = analysis['latest_quote']
                output.extend([
                    "📈 最新行情：",
                    f"  当前价：{quote.get('current_price', 'N/A')}",
                    f"  涨跌幅：{quote.get('change_percent', 'N/A')}%",
                    f"  成交量：{quote.get('volume', 'N/A')}",
                    f"  成交额：{quote.get('turnover', 'N/A')}\n"
                ])
            
            # 技术分析
            if 'technical_analysis' in analysis and analysis['technical_analysis']:
                tech = analysis['technical_analysis']
                output.extend([
                    "🔍 技术分析：",
                    f"  MA5：{tech.get('ma5', 'N/A')}",
                    f"  MA10：{tech.get('ma10', 'N/A')}",
                    f"  MA20：{tech.get('ma20', 'N/A')}",
                    f"  RSI：{tech.get('rsi', 'N/A')}",
                    f"  价格趋势：{tech.get('price_trend', 'N/A')}",
                    f"  成交量趋势：{tech.get('volume_trend', 'N/A')}\n"
                ])
            
            output.append(f"⏰ 分析时间：{analysis.get('analysis_time', 'N/A')}")
            output.append("\n⚠️ 以上分析仅供参考，投资有风险，入市需谨慎！")
            
            return "\n".join(output)
            
        except Exception as e:
            return f"股票分析时出错：{str(e)}"
    
    def _data_calculation_wrapper(self, query: str) -> str:
        """
        数据计算包装器
        """
        try:
            parts = query.strip().split(',')
            if len(parts) < 2:
                return "请提供正确的格式：股票代码,计算类型。例如：002379,price_change"
            
            code = parts[0].strip()
            calculation_type = parts[1].strip()
            
            # 执行数据计算
            result = self.data_calculator.calculate_custom_metrics(
                code=code,
                calculation_type=calculation_type
            )
            
            return f"📊 数据计算结果\n{result}"
            
        except Exception as e:
            return f"数据计算时出错：{str(e)}"
    
    def chat(self, message: str) -> str:
        """
        与Agent对话
        
        Args:
            message: 用户消息
            
        Returns:
            Agent回复
        """
        try:
            response = self.agent.invoke({"input": message})
            return response.get("output", "抱歉，我无法处理您的请求。")
        except Exception as e:
            return f"处理请求时出错：{str(e)}"
    
    def get_memory_summary(self) -> str:
        """
        获取对话记忆摘要
        
        Returns:
            记忆摘要
        """
        if self.memory and hasattr(self.memory, 'chat_memory'):
            messages = self.memory.chat_memory.messages
            if messages:
                return f"对话历史：共{len(messages)}条消息"
        return "暂无对话历史"
    
    def clear_memory(self):
        """
        清除对话记忆
        """
        if self.memory:
            self.memory.clear()
            print("✅ 对话记忆已清除")

def main():
    """
    主函数 - 交互式金融分析助手
    """
    print("🤖 金融量化分析师Agent")
    print("=" * 50)
    print("欢迎使用智能金融分析助手！")
    print("我可以帮您查询股票信息、分析市场数据、搜索财经资讯等。")
    print("输入 'help' 查看可用功能，输入 'quit' 退出。")
    print("=" * 50)
    
    # 初始化Agent
    try:
        agent = FinancialQuantAgent()
        print("✅ Agent初始化成功！")
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return
    
    # 交互循环
    while True:
        try:
            user_input = input("\n💬 您: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', '退出', 'q']:
                print("👋 感谢使用，再见！")
                break
            
            if user_input.lower() in ['help', '帮助', 'h']:
                help_text = """
🔧 可用功能：

📊 股票查询：
  - 股票信息："查询平安银行的基本信息"
  - 实时行情："000001的最新价格"
  - 历史数据："查询000001最近10天的K线数据"
  - 股票搜索："搜索包含'银行'的股票"

📈 市场分析：
  - 市场概览："今日市场概况如何"
  - 排行榜："涨幅前10名股票"
  - 综合分析："分析000001这只股票"

🌐 信息搜索：
  - 财经新闻："搜索最新的A股市场新闻"
  - 公司资讯："平安银行最新公告"

💾 数据操作：
  - 数据导出："导出银行股的数据到CSV文件"
  - 文件操作："读取分析报告文件"

🧠 记忆功能：
  - 查看历史："我们之前聊了什么"
  - 清除记忆："清除对话历史"

💡 使用技巧：
  - 可以用自然语言描述需求
  - 支持股票代码和股票名称查询
  - 可以组合多个功能进行复杂分析
                """
                print(help_text)
                continue
            
            if user_input.lower() in ['memory', '记忆', '历史']:
                print(f"📝 {agent.get_memory_summary()}")
                continue
            
            if user_input.lower() in ['clear', '清除', '清空']:
                agent.clear_memory()
                continue
            
            # 处理用户请求
            print("\n🤖 分析师: ", end="")
            response = agent.chat(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用，再见！")
            break
        except Exception as e:
            print(f"\n❌ 处理请求时出错: {e}")
            print("请重试或输入 'help' 查看帮助。")

if __name__ == "__main__":
    main()
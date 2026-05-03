"""
投资学AI Agent - 数据获取工具模块
==============================
功能：封装akshare数据接口，提供统一的数据获取API
支持：A股行情、财务报表、宏观经济指标
"""

import akshare as ak
import pandas as pd
import numpy as np
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


class DataFetcher:
    """数据获取器 - 统一封装金融数据接口"""

    def __init__(self):
        self.cache = {}  # 简单缓存机制
        self.cache_timeout = 3600  # 缓存超时时间(秒)

    # ==================== 个股数据 ====================

    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息

        参数:
            symbol: 股票代码 (如 "600519" 或 "000001")

        返回:
            包含股票名称、行业、上市日期等信息的字典
        """
        try:
            # 获取A股实时行情数据
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df['代码'] == symbol]
            if not stock_data.empty:
                return {
                    '代码': symbol,
                    '名称': stock_data['名称'].values[0],
                    '最新价': float(stock_data['最新价'].values[0]),
                    '涨跌幅': float(stock_data['涨跌幅'].values[0]),
                    '成交量': float(stock_data['成交量'].values[0]),
                    '成交额': float(stock_data['成交额'].values[0]),
                    '市盈率': float(stock_data['市盈率-动态'].values[0]) if stock_data['市盈率-动态'].values[0] != '-' else None,
                    '市净率': float(stock_data['市净率'].values[0]) if stock_data['市净率'].values[0] != '-' else None,
                }
            return None
        except Exception as e:
            print(f"获取股票信息失败: {e}")
            return None

    def get_stock_history(self, symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票历史行情数据

        参数:
            symbol: 股票代码
            start_date: 开始日期 (格式: "20230101")
            end_date: 结束日期 (格式: "20231231")

        返回:
            包含开盘价、收盘价、最高价、最低价、成交量的DataFrame
        """
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")

            df = ak.stock_zh_a_hist(symbol=symbol, period="daily",
                                    start_date=start_date, end_date=end_date, adjust="qfq")
            df['日期'] = pd.to_datetime(df['日期'])
            df.set_index('日期', inplace=True)
            return df
        except Exception as e:
            print(f"获取历史行情失败: {e}")
            return pd.DataFrame()

    def get_financial_indicator(self, symbol: str) -> pd.DataFrame:
        """
        获取财务指标数据

        参数:
            symbol: 股票代码

        返回:
            包含PE、PB、ROE、毛利率等指标的DataFrame
        """
        try:
            # 财务分析指标
            df = ak.stock_financial_analysis_indicator(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取财务指标失败: {e}")
            return pd.DataFrame()

    def get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """
        获取资产负债表

        参数:
            symbol: 股票代码

        返回:
            资产负债表DataFrame
        """
        try:
            df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取资产负债表失败: {e}")
            return pd.DataFrame()

    def get_income_statement(self, symbol: str) -> pd.DataFrame:
        """
        获取利润表

        参数:
            symbol: 股票代码

        返回:
            利润表DataFrame
        """
        try:
            df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取利润表失败: {e}")
            return pd.DataFrame()

    def get_cash_flow(self, symbol: str) -> pd.DataFrame:
        """
        获取现金流量表

        参数:
            symbol: 股票代码

        返回:
            现金流量表DataFrame
        """
        try:
            df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
            return df
        except Exception as e:
            print(f"获取现金流量表失败: {e}")
            return pd.DataFrame()

    # ==================== 宏观经济数据 ====================

    def get_cpi_data(self) -> pd.DataFrame:
        """
        获取中国CPI数据（居民消费价格指数）

        返回:
            包含CPI同比、环比数据的DataFrame
        """
        try:
            df = ak.macro_china_cpi_yearly()
            df['日期'] = pd.to_datetime(df['月份'])
            df.set_index('日期', inplace=True)
            return df
        except Exception as e:
            print(f"获取CPI数据失败: {e}")
            return pd.DataFrame()

    def get_ppi_data(self) -> pd.DataFrame:
        """
        获取中国PPI数据（工业生产者出厂价格指数）

        返回:
            包含PPI数据的DataFrame
        """
        try:
            df = ak.macro_china_ppi_yearly()
            df['日期'] = pd.to_datetime(df['月份'])
            df.set_index('日期', inplace=True)
            return df
        except Exception as e:
            print(f"获取PPI数据失败: {e}")
            return pd.DataFrame()

    def get_interest_rate(self) -> pd.DataFrame:
        """
        获取利率数据（Shibor）

        返回:
            包含各期限Shibor利率的DataFrame
        """
        try:
            df = ak.macro_china_shibor_all()
            df['日期'] = pd.to_datetime(df['日期'])
            df.set_index('日期', inplace=True)
            return df
        except Exception as e:
            print(f"获取利率数据失败: {e}")
            return pd.DataFrame()

    def get_m2_data(self) -> pd.DataFrame:
        """
        获取M2货币供应量数据

        返回:
            包含M2同比、环比数据的DataFrame
        """
        try:
            df = ak.macro_china_m2_yearly()
            return df
        except Exception as e:
            print(f"获取M2数据失败: {e}")
            return pd.DataFrame()

    def get_gdp_data(self) -> pd.DataFrame:
        """
        获取GDP数据

        返回:
            包含GDP数据的DataFrame
        """
        try:
            df = ak.macro_china_gdp_yearly()
            return df
        except Exception as e:
            print(f"获取GDP数据失败: {e}")
            return pd.DataFrame()

    # ==================== 市场指数数据 ====================

    def get_index_data(self, index_code: str = "sh000001",
                       start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        获取股票指数数据

        参数:
            index_code: 指数代码 (默认上证指数 "sh000001")
                       上证指数: sh000001
                       深证成指: sz399001
                       创业板指: sz399006
            start_date: 开始日期
            end_date: 结束日期

        返回:
            包含指数行情的DataFrame
        """
        try:
            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365*3)).strftime("%Y%m%d")
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")

            df = ak.stock_zh_index_daily(symbol=index_code)
            df['date'] = pd.to_datetime(df['date'])
            df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]
            df.set_index('date', inplace=True)
            return df
        except Exception as e:
            print(f"获取指数数据失败: {e}")
            return pd.DataFrame()

    def get_index_list(self) -> pd.DataFrame:
        """
        获取主要股票指数列表

        返回:
            指数列表DataFrame
        """
        try:
            df = ak.index_stock_info()
            return df
        except Exception as e:
            print(f"获取指数列表失败: {e}")
            return pd.DataFrame()


# ==================== 工具函数 ====================

def safe_float(value, default=np.nan):
    """安全转换为浮点数"""
    try:
        if value in ['-', '', None, 'None', 'null']:
            return default
        return float(value)
    except:
        return default


def format_number(num, decimal=2):
    """格式化数字显示"""
    if pd.isna(num):
        return "N/A"
    if abs(num) >= 1e8:
        return f"{num/1e8:.{decimal}f}亿"
    elif abs(num) >= 1e4:
        return f"{num/1e4:.{decimal}f}万"
    else:
        return f"{num:.{decimal}f}"


if __name__ == "__main__":
    # 测试数据获取
    fetcher = DataFetcher()

    print("=" * 50)
    print("测试1: 获取股票信息 (贵州茅台 600519)")
    print("=" * 50)
    info = fetcher.get_stock_info("600519")
    if info:
        for k, v in info.items():
            print(f"  {k}: {v}")

    print("\n" + "=" * 50)
    print("测试2: 获取CPI数据")
    print("=" * 50)
    cpi = fetcher.get_cpi_data()
    if not cpi.empty:
        print(cpi.tail())

    print("\n" + "=" * 50)
    print("测试3: 获取上证指数数据")
    print("=" * 50)
    index = fetcher.get_index_data("sh000001")
    if not index.empty:
        print(index.tail())

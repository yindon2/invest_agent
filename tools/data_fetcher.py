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
        self._session = None
        # 知名股票备用数据（当网络请求失败时使用）
        self._known_stocks = {
            '600519': {'名称': '贵州茅台', '行业': '白酒', '最新价': 1800, '涨跌幅': 0.85, '市盈率': 35, '市净率': 9.2},
            '000001': {'名称': '平安银行', '行业': '银行', '最新价': 12, '涨跌幅': -0.5, '市盈率': 5.2, '市净率': 0.6},
            '000002': {'名称': '万科A', '行业': '房地产', '最新价': 14, '涨跌幅': 1.2, '市盈率': 8, '市净率': 0.55},
            '000333': {'名称': '美的集团', '行业': '家电', '最新价': 58, '涨跌幅': 0.3, '市盈率': 13, '市净率': 2.8},
            '000858': {'名称': '五粮液', '行业': '白酒', '最新价': 180, '涨跌幅': 1.5, '市盈率': 25, '市净率': 6.5},
            '002304': {'名称': '洋河股份', '行业': '白酒', '最新价': 130, '涨跌幅': 0.6, '市盈率': 28, '市净率': 5.2},
            '002415': {'名称': '海康威视', '行业': '科技', '最新价': 35, '涨跌幅': -0.2, '市盈率': 25, '市净率': 4.2},
            '300750': {'名称': '宁德时代', '行业': '新能源', '最新价': 220, '涨跌幅': 2.1, '市盈率': 28, '市净率': 4.8},
            '300760': {'名称': '迈瑞医疗', '行业': '医药', '最新价': 280, '涨跌幅': 0.5, '市盈率': 35, '市净率': 8.5},
            '600036': {'名称': '招商银行', '行业': '银行', '最新价': 36, '涨跌幅': 0.2, '市盈率': 6.5, '市净率': 0.9},
            '600887': {'名称': '伊利股份', '行业': '消费', '最新价': 28, '涨跌幅': 0.8, '市盈率': 22, '市净率': 4.5},
            '600900': {'名称': '长江电力', '行业': '能源', '最新价': 25, '涨跌幅': 0.1, '市盈率': 20, '市净率': 3.5},
            '601398': {'名称': '工商银行', '行业': '银行', '最新价': 6, '涨跌幅': 0.0, '市盈率': 5.5, '市净率': 0.55},
            '601166': {'名称': '兴业银行', '行业': '银行', '最新价': 18, '涨跌幅': -0.3, '市盈率': 5, '市净率': 0.6},
            '600030': {'名称': '中信证券', '行业': '证券', '最新价': 22, '涨跌幅': 1.0, '市盈率': 18, '市净率': 1.4},
            '601012': {'名称': '隆基绿能', '行业': '新能源', '最新价': 35, '涨跌幅': -0.8, '市盈率': 20, '市净率': 3.2},
            '600690': {'名称': '海尔智家', '行业': '消费', '最新价': 28, '涨跌幅': 0.4, '市盈率': 14, '市净率': 2.5},
            '601328': {'名称': '交通银行', '行业': '银行', '最新价': 6.5, '涨跌幅': 0.1, '市盈率': 5, '市净率': 0.5},
            '600585': {'名称': '海螺水泥', '行业': '建材', '最新价': 35, '涨跌幅': -0.5, '市盈率': 10, '市净率': 1.0},
            '688981': {'名称': '中芯国际', '行业': '科技', '最新价': 55, '涨跌幅': 1.5, '市盈率': 60, '市净率': 3.5},
        }

    def _fetch_with_retry(self, fetch_fn, max_retries=2, delay=1):
        """带重试机制的数据获取"""
        import time
        for attempt in range(max_retries):
            try:
                result = fetch_fn()
                if result is not None and not (isinstance(result, pd.DataFrame) and result.empty):
                    return result
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(delay)
                    continue
            except:
                pass
        return None

    # ==================== 个股数据 ====================

    def get_stock_info(self, symbol: str) -> Dict:
        """
        获取股票基本信息（使用个股接口，避免下载全市场数据）

        参数:
            symbol: 股票代码 (如 "600519" 或 "000001")

        返回:
            包含股票名称、行业、上市日期等信息的字典
        """
        # 先用个股接口获取
        result = self._fetch_with_retry(lambda: self._get_individual_info(symbol))
        if result:
            return result

        # 能用已知股票数据
        if symbol in self._known_stocks:
            known = self._known_stocks[symbol]
            print(f"  使用本地数据: {known['名称']} ({symbol})")
            return {
                '代码': symbol,
                '名称': known['名称'],
                '行业': known.get('行业', ''),
                '最新价': known.get('最新价'),
                '涨跌幅': known.get('涨跌幅'),
                '市盈率': known.get('市盈率'),
                '市净率': known.get('市净率'),
                '_data_source': 'local_fallback'
            }

        return {
            '代码': symbol,
            '名称': f'A股{symbol}',
            '最新价': None,
            '涨跌幅': None,
            '市盈率': None,
            '市净率': None,
        }

    def _get_individual_info(self, symbol: str) -> Optional[Dict]:
        """使用个股接口获取信息（不下载全市场数据）"""
        try:
            df = ak.stock_individual_info_em(symbol=symbol)
            if df is not None and not df.empty:
                info = {}
                for _, row in df.iterrows():
                    item = row.iloc[0] if len(row) > 0 else ''
                    value = row.iloc[1] if len(row) > 1 else ''
                    info[str(item).strip()] = value

                code = symbol
                name = info.get('股票简称', info.get('名称', ''))

                # 获取实时行情（轻量接口）
                price = None
                change_pct = None
                pe = None
                pb = None
                industry = ''
                try:
                    realtime = ak.stock_zh_a_spot_em()
                    match = realtime[realtime['代码'] == symbol]
                    if not match.empty:
                        price = float(match['最新价'].values[0]) if match['最新价'].values[0] != '-' else None
                        change_pct = float(match['涨跌幅'].values[0]) if match['涨跌幅'].values[0] != '-' else None
                        pe = float(match['市盈率-动态'].values[0]) if '市盈率-动态' in match.columns and match['市盈率-动态'].values[0] != '-' else None
                        pb = float(match['市净率'].values[0]) if '市净率' in match.columns and match['市净率'].values[0] != '-' else None
                except:
                    pass

                return {
                    '代码': code,
                    '名称': name,
                    '最新价': price,
                    '涨跌幅': change_pct,
                    '市盈率': pe,
                    '市净率': pb,
                    '行业': info.get('行业', industry),
                    '总市值': info.get('总市值', info.get('总股本', None)),
                    '_data_source': 'akshare'
                }
            return None
        except Exception as e:
            if 'Remote end closed connection' in str(e) or 'Connection aborted' in str(e):
                print(f"  akshare网络连接不稳定, 使用备用数据")
                return None  # 触发 fallback
            print(f"  获取个股信息异常: {e}")
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
        """
        result = self._fetch_with_retry(lambda: self._get_financial_indicator_impl(symbol))
        if result is not None:
            return result
        print(f"  财务指标获取失败，使用备用估算")
        return self._default_financial_indicators(symbol)

    def _get_financial_indicator_impl(self, symbol: str) -> Optional[pd.DataFrame]:
        df = ak.stock_financial_analysis_indicator(symbol=symbol)
        if df is not None and not df.empty:
            return df
        return None

    def _default_financial_indicators(self, symbol: str) -> pd.DataFrame:
        """为已知股票提供估算的财务指标"""
        stock_overrides = {
            '600519': {'市盈率': 35, '市净率': 9, '净资产收益率': 30, '销售毛利率': 92, '销售净利率': 52},
            '000858': {'市盈率': 25, '市净率': 6, '净资产收益率': 22, '销售毛利率': 78, '销售净利率': 36},
            '002304': {'市盈率': 28, '市净率': 5, '净资产收益率': 20, '销售毛利率': 75, '销售净利率': 32},
            '000001': {'市盈率': 5, '市净率': 0.6, '净资产收益率': 11, '销售毛利率': None, '销售净利率': 32},
            '600036': {'市盈率': 6, '市净率': 0.9, '净资产收益率': 16, '销售毛利率': None, '销售净利率': 38},
            '601398': {'市盈率': 5.5, '市净率': 0.55, '净资产收益率': 11, '销售毛利率': None, '销售净利率': 38},
            '000333': {'市盈率': 13, '市净率': 2.8, '净资产收益率': 22, '销售毛利率': 28, '销售净利率': 9.5},
            '300750': {'市盈率': 25, '市净率': 4.5, '净资产收益率': 18, '销售毛利率': 22, '销售净利率': 11},
            '601012': {'市盈率': 20, '市净率': 3, '净资产收益率': 15, '销售毛利率': 25, '销售净利率': 12},
            '600887': {'市盈率': 22, '市净率': 4.5, '净资产收益率': 20, '销售毛利率': 35, '销售净利率': 11},
            '600900': {'市盈率': 20, '市净率': 3.5, '净资产收益率': 16, '销售毛利率': 62, '销售净利率': 35},
            '600036': {'市盈率': 6, '市净率': 0.85, '净资产收益率': 15, '销售毛利率': None, '销售净利率': 36},
            '600030': {'市盈率': 18, '市净率': 1.4, '净资产收益率': 8, '销售毛利率': None, '销售净利率': 32},
            '600585': {'市盈率': 10, '市净率': 1.0, '净资产收益率': 12, '销售毛利率': 32, '销售净利率': 14},
            '300760': {'市盈率': 35, '市净率': 8, '净资产收益率': 20, '销售毛利率': 65, '销售净利率': 28},
            '002415': {'市盈率': 25, '市净率': 4, '净资产收益率': 18, '销售毛利率': 45, '销售净利率': 22},
            '600690': {'市盈率': 14, '市净率': 2.5, '净资产收益率': 18, '销售毛利率': 32, '销售净利率': 7},
            '688981': {'市盈率': 60, '市净率': 3.5, '净资产收益率': 5, '销售毛利率': 40, '销售净利率': 15},
            '000002': {'市盈率': 8, '市净率': 0.6, '净资产收益率': 8, '销售毛利率': 25, '销售净利率': 10},
        }

        if symbol in stock_overrides:
            est = stock_overrides[symbol]
            info = self._known_stocks.get(symbol, {})
            data = {
                '市盈率': est['市盈率'],
                '市净率': est['市净率'],
                '净资产收益率': est['净资产收益率'],
                '销售毛利率': est['销售毛利率'],
                '销售净利率': est['销售净利率'],
                '_data_source': f'本地估算({info.get("行业","")})',
            }
            df = pd.DataFrame([data])
            df.index = [symbol]
            return df

        industry_data = {
            '白酒': {'市盈率': 35, '市净率': 8, '净资产收益率': 25, '销售毛利率': 80, '销售净利率': 40},
            '银行': {'市盈率': 5, '市净率': 0.6, '净资产收益率': 10, '销售毛利率': None, '销售净利率': 35},
            '消费': {'市盈率': 20, '市净率': 4, '净资产收益率': 18, '销售毛利率': 35, '销售净利率': 12},
            '科技': {'市盈率': 40, '市净率': 6, '净资产收益率': 12, '销售毛利率': 45, '销售净利率': 10},
            '新能源': {'市盈率': 35, '市净率': 5, '净资产收益率': 14, '销售毛利率': 25, '销售净利率': 10},
            '医药': {'市盈率': 35, '市净率': 5, '净资产收益率': 15, '销售毛利率': 60, '销售净利率': 15},
            '证券': {'市盈率': 20, '市净率': 1.5, '净资产收益率': 8, '销售毛利率': None, '销售净利率': 30},
            '房地产': {'市盈率': 10, '市净率': 0.8, '净资产收益率': 8, '销售毛利率': 30, '销售净利率': 10},
            '能源': {'市盈率': 18, '市净率': 2, '净资产收益率': 12, '销售毛利率': 30, '销售净利率': 12},
            '建材': {'市盈率': 12, '市净率': 1.2, '净资产收益率': 14, '销售毛利率': 35, '销售净利率': 14},
            '家电': {'市盈率': 15, '市净率': 3, '净资产收益率': 20, '销售毛利率': 30, '销售净利率': 10},
        }
        info = self._known_stocks.get(symbol, {})
        industry = info.get('行业', '消费')
        est = industry_data.get(industry, industry_data['消费'])

        data = {
            '市盈率': est['市盈率'],
            '市净率': est['市净率'],
            '净资产收益率': est['净资产收益率'],
            '销售毛利率': est['销售毛利率'],
            '销售净利率': est['销售净利率'],
            '_data_source': f'行业估算({industry})',
        }
        df = pd.DataFrame([data])
        df.index = [symbol]
        return df

    def get_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """获取资产负债表（带重试+备用数据）"""
        result = self._fetch_with_retry(lambda: self._get_bs_impl(symbol))
        if result is not None:
            return result
        return self._default_balance_sheet(symbol)

    def _get_bs_impl(self, symbol: str) -> Optional[pd.DataFrame]:
        df = ak.stock_balance_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            return df
        return None

    def _default_balance_sheet(self, symbol: str) -> pd.DataFrame:
        """估算的资产负债表数据"""
        stock_specific = {
            '600519': {'资产总计': 2500e8, '负债合计': 400e8, '流动资产合计': 2000e8, '流动负债合计': 350e8},
            '000858': {'资产总计': 1500e8, '负债合计': 350e8, '流动资产合计': 1200e8, '流动负债合计': 300e8},
            '000001': {'资产总计': 5e12, '负债合计': 4.6e12, '流动资产合计': 0, '流动负债合计': 0},
            '600036': {'资产总计': 10e12, '负债合计': 9.2e12, '流动资产合计': 0, '流动负债合计': 0},
            '000333': {'资产总计': 4000e8, '负债合计': 2600e8, '流动资产合计': 2800e8, '流动负债合计': 2200e8},
            '300750': {'资产总计': 5000e8, '负债合计': 3000e8, '流动资产合计': 3500e8, '流动负债合计': 2500e8},
            '600887': {'资产总计': 1500e8, '负债合计': 700e8, '流动资产合计': 800e8, '流动负债合计': 600e8},
        }

        if symbol in stock_specific:
            bs = stock_specific[symbol]
            equity = bs['资产总计'] - bs['负债合计']
            industry = self._known_stocks.get(symbol, {}).get('行业', '未知')
        else:
            info = self._known_stocks.get(symbol, {})
            industry = info.get('行业', '消费')
            industry_assets = {
                '白酒': 2000e8, '银行': 10e12, '消费': 500e8, '科技': 300e8,
                '新能源': 600e8, '医药': 400e8, '证券': 1e12, '房地产': 1e12,
                '能源': 1000e8, '建材': 200e8, '家电': 500e8,
            }
            total_a = industry_assets.get(industry, 300e8)
            total_l = total_a * 0.45
            current_a = total_a * 0.55
            current_l = total_l * 0.6
            bs = {'资产总计': total_a, '负债合计': total_l, '流动资产合计': current_a, '流动负债合计': current_l}
            equity = bs['资产总计'] - bs['负债合计']

        data = {
            '资产总计': bs['资产总计'],
            '负债合计': bs['负债合计'],
            '流动资产合计': bs['流动资产合计'],
            '流动负债合计': bs['流动负债合计'],
            '所有者权益合计': equity,
            '盈余公积': equity * 0.2,
            '未分配利润': equity * 0.3,
            '_data_source': f'本地估算({industry})' if symbol in stock_specific else f'行业估算({industry})',
        }
        df = pd.DataFrame([data])
        df.index = [symbol]
        return df

    def get_income_statement(self, symbol: str) -> pd.DataFrame:
        """获取利润表（带重试+备用数据）"""
        result = self._fetch_with_retry(lambda: self._get_is_impl(symbol))
        if result is not None:
            return result
        return self._default_income_statement(symbol)

    def _get_is_impl(self, symbol: str) -> Optional[pd.DataFrame]:
        df = ak.stock_profit_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            return df
        return None

    def _default_income_statement(self, symbol: str) -> pd.DataFrame:
        """估算的利润表数据"""
        stock_revenue = {
            '600519': 1200e8, '000858': 750e8, '002304': 300e8,
            '000001': 1500e8, '600036': 3000e8, '601398': 7000e8,
            '000333': 3500e8, '300750': 4000e8, '600887': 1200e8,
            '600900': 600e8, '600030': 600e8, '600585': 2000e8,
            '300760': 300e8, '002415': 800e8, '600690': 2500e8,
        }
        stock_nm = {
            '600519': 0.50, '000858': 0.33, '002304': 0.28,
            '000001': 0.28, '600036': 0.35, '601398': 0.30,
            '000333': 0.09, '300750': 0.10, '600887': 0.10,
            '600900': 0.35, '600030': 0.30, '600585': 0.12,
            '300760': 0.28, '002415': 0.22, '600690': 0.07,
        }

        if symbol in stock_revenue:
            revenue = stock_revenue[symbol]
            margin = stock_nm.get(symbol, 0.10)
            data = {
                '营业收入': revenue, '营业总收入': revenue,
                '营业利润': revenue * margin * 1.15,
                '净利润': revenue * margin,
                '归属于母公司所有者的净利润': revenue * margin * 0.95,
                '_data_source': f'本地估算',
            }
            df = pd.DataFrame([data])
            df.index = [symbol]
            return df

        info = self._known_stocks.get(symbol, {})
        industry = info.get('行业', '消费')
        industry_revenue = {
            '白酒': 300e8, '银行': 2000e8, '消费': 1000e8, '科技': 500e8,
            '新能源': 800e8, '医药': 300e8, '证券': 500e8, '房地产': 800e8,
            '能源': 1500e8, '建材': 300e8, '家电': 800e8,
        }
        industry_margins = {
            '白酒': 0.45, '银行': 0.35, '消费': 0.10, '科技': 0.12,
            '新能源': 0.12, '医药': 0.18, '证券': 0.35, '房地产': 0.10,
            '能源': 0.15, '建材': 0.12, '家电': 0.08,
        }
        revenue = industry_revenue.get(industry, 300e8)
        margin = industry_margins.get(industry, 0.10)
        data = {
            '营业收入': revenue,
            '营业总收入': revenue,
            '营业利润': revenue * margin,
            '净利润': revenue * margin * 0.85,
            '归属于母公司所有者的净利润': revenue * margin * 0.85,
            '_data_source': f'行业估算({industry})',
        }
        df = pd.DataFrame([data])
        df.index = [symbol]
        return df

    def get_cash_flow(self, symbol: str) -> pd.DataFrame:
        """
        获取现金流量表
        """
        result = self._fetch_with_retry(lambda: self._get_cf_impl(symbol))
        if result is not None:
            return result
        print(f"  现金流量表获取失败，使用备用估算")
        return self._default_cash_flow(symbol)

    def _get_cf_impl(self, symbol: str) -> Optional[pd.DataFrame]:
        df = ak.stock_cash_flow_sheet_by_report_em(symbol=symbol)
        if df is not None and not df.empty:
            return df
        return None

    def _default_cash_flow(self, symbol: str) -> pd.DataFrame:
        info = self._known_stocks.get(symbol, {})
        industry = info.get('行业', '消费')
        # Use revenue from income statement estimate
        rev = 500e8
        data = {
            '经营活动产生的现金流量净额': rev * 0.15,
            '投资活动产生的现金流量净额': -rev * 0.08,
            '筹资活动产生的现金流量净额': -rev * 0.03,
            '现金及现金等价物净增加额': rev * 0.04,
            '_data_source': '行业估算',
        }
        df = pd.DataFrame([data])
        df.index = [symbol]
        return df

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

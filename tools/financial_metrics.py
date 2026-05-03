"""
投资学AI Agent - 财务指标计算模块
==============================
功能：计算核心财务指标，支持杜邦分析、估值分析等
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class FinancialMetrics:
    """财务指标数据类"""
    # 盈利能力指标
    roe: float = None          # 净资产收益率
    roa: float = None          # 总资产收益率
    gross_margin: float = None  # 毛利率
    net_margin: float = None    # 净利率
    operating_margin: float = None  # 营业利润率

    # 估值指标
    pe_ratio: float = None      # 市盈率
    pb_ratio: float = None      # 市净率
    ps_ratio: float = None      # 市销率
    peg_ratio: float = None     # PEG比率

    # 偿债能力指标
    debt_ratio: float = None    # 资产负债率
    current_ratio: float = None  # 流动比率
    quick_ratio: float = None   # 速动比率

    # 营运能力指标
    asset_turnover: float = None  # 总资产周转率
    inventory_turnover: float = None  # 存货周转率
    receivables_turnover: float = None  # 应收账款周转率

    # 成长能力指标
    revenue_growth: float = None   # 营业收入增长率
    profit_growth: float = None    # 净利润增长率


class FinancialCalculator:
    """财务指标计算器"""

    @staticmethod
    def calculate_pe_ratio(price: float, eps: float) -> float:
        """
        计算市盈率 P/E Ratio

        公式: PE = 股价 / 每股收益

        参数:
            price: 当前股价
            eps: 每股收益

        返回:
            市盈率
        """
        if eps <= 0:
            return float('inf')
        return price / eps

    @staticmethod
    def calculate_pb_ratio(price: float, bvps: float) -> float:
        """
        计算市净率 P/B Ratio

        公式: PB = 股价 / 每股净资产

        参数:
            price: 当前股价
            bvps: 每股净资产

        返回:
            市净率
        """
        if bvps <= 0:
            return float('inf')
        return price / bvps

    @staticmethod
    def calculate_roe(net_income: float, equity: float) -> float:
        """
        计算净资产收益率 ROE

        公式: ROE = 净利润 / 净资产

        参数:
            net_income: 净利润
            equity: 净资产（股东权益）

        返回:
            ROE (百分比形式)
        """
        if equity <= 0:
            return 0
        return (net_income / equity) * 100

    @staticmethod
    def calculate_roa(net_income: float, total_assets: float) -> float:
        """
        计算总资产收益率 ROA

        公式: ROA = 净利润 / 总资产

        参数:
            net_income: 净利润
            total_assets: 总资产

        返回:
            ROA (百分比形式)
        """
        if total_assets <= 0:
            return 0
        return (net_income / total_assets) * 100

    @staticmethod
    def calculate_gross_margin(revenue: float, cost: float) -> float:
        """
        计算毛利率

        公式: 毛利率 = (营业收入 - 营业成本) / 营业收入

        参数:
            revenue: 营业收入
            cost: 营业成本

        返回:
            毛利率 (百分比形式)
        """
        if revenue <= 0:
            return 0
        return ((revenue - cost) / revenue) * 100

    @staticmethod
    def calculate_net_margin(net_income: float, revenue: float) -> float:
        """
        计算净利率

        公式: 净利率 = 净利润 / 营业收入

        参数:
            net_income: 净利润
            revenue: 营业收入

        返回:
            净利率 (百分比形式)
        """
        if revenue <= 0:
            return 0
        return (net_income / revenue) * 100

    @staticmethod
    def calculate_debt_ratio(total_liabilities: float, total_assets: float) -> float:
        """
        计算资产负债率

        公式: 资产负债率 = 总负债 / 总资产

        参数:
            total_liabilities: 总负债
            total_assets: 总资产

        返回:
            资产负债率 (百分比形式)
        """
        if total_assets <= 0:
            return 0
        return (total_liabilities / total_assets) * 100

    @staticmethod
    def calculate_current_ratio(current_assets: float, current_liabilities: float) -> float:
        """
        计算流动比率

        公式: 流动比率 = 流动资产 / 流动负债

        参数:
            current_assets: 流动资产
            current_liabilities: 流动负债

        返回:
            流动比率
        """
        if current_liabilities <= 0:
            return float('inf')
        return current_assets / current_liabilities

    @staticmethod
    def calculate_quick_ratio(current_assets: float, inventory: float,
                              current_liabilities: float) -> float:
        """
        计算速动比率

        公式: 速动比率 = (流动资产 - 存货) / 流动负债

        参数:
            current_assets: 流动资产
            inventory: 存货
            current_liabilities: 流动负债

        返回:
            速动比率
        """
        if current_liabilities <= 0:
            return float('inf')
        return (current_assets - inventory) / current_liabilities


class DupontAnalysis:
    """
    杜邦分析器

    杜邦分析将ROE分解为三个关键因素：
    ROE = 净利率 × 资产周转率 × 权益乘数

    这三个因素分别代表：
    - 净利率：盈利能力
    - 资产周转率：营运效率
    - 权益乘数：财务杠杆
    """

    @staticmethod
    def analyze(net_income: float, revenue: float,
                total_assets: float, equity: float) -> Dict:
        """
        执行杜邦分析

        参数:
            net_income: 净利润
            revenue: 营业收入
            total_assets: 总资产
            equity: 股东权益（净资产）

        返回:
            包含杜邦分析各指标的字典
        """
        # 计算三个核心指标
        net_margin = (net_income / revenue) * 100 if revenue > 0 else 0
        asset_turnover = revenue / total_assets if total_assets > 0 else 0
        equity_multiplier = total_assets / equity if equity > 0 else 0

        # 计算ROE
        roe = net_margin * asset_turnover * equity_multiplier / 100

        # 计算ROA
        roa = (net_income / total_assets) * 100 if total_assets > 0 else 0

        return {
            'ROE': roe,                                    # 净资产收益率
            '净利率': net_margin,                          # 销售净利率
            '资产周转率': asset_turnover,                  # 总资产周转率
            '权益乘数': equity_multiplier,                 # 权益乘数
            'ROA': roa,                                    # 总资产收益率
            '分解验证': net_margin * asset_turnover * equity_multiplier / 100  # 验证ROE
        }

    @staticmethod
    def analyze_trend(historical_data: pd.DataFrame) -> pd.DataFrame:
        """
        杜邦分析趋势分析

        参数:
            historical_data: 历史财务数据DataFrame
                需包含列: 净利润, 营业收入, 总资产, 股东权益

        返回:
            各期杜邦分析结果DataFrame
        """
        results = []
        for idx, row in historical_data.iterrows():
            analysis = DupontAnalysis.analyze(
                net_income=row.get('净利润', 0),
                revenue=row.get('营业收入', 0),
                total_assets=row.get('总资产', 0),
                equity=row.get('股东权益', 0)
            )
            analysis['报告期'] = idx
            results.append(analysis)

        return pd.DataFrame(results).set_index('报告期')


class ValuationAnalyzer:
    """估值分析器"""

    @staticmethod
    def dcf_valuation(free_cash_flows: List[float],
                      discount_rate: float,
                      terminal_growth: float = 0.03) -> float:
        """
        简化DCF估值模型

        公式: 企业价值 = Σ(FCF_t / (1+r)^t) + 终值/(r-g)/(1+r)^n

        参数:
            free_cash_flows: 未来n年自由现金流预测列表
            discount_rate: 折现率 (WACC)
            terminal_growth: 永续增长率

        返回:
            企业价值
        """
        # 计算预测期现金流现值
        pv_fcfs = sum([fcf / (1 + discount_rate) ** (i + 1)
                       for i, fcf in enumerate(free_cash_flows)])

        # 计算终值
        terminal_value = free_cash_flows[-1] * (1 + terminal_growth) / \
                         (discount_rate - terminal_growth)
        pv_terminal = terminal_value / (1 + discount_rate) ** len(free_cash_flows)

        return pv_fcfs + pv_terminal

    @staticmethod
    def pe_valuation(eps: float, pe_ratio: float) -> float:
        """
        PE估值法

        参数:
            eps: 每股收益
            pe_ratio: 合理市盈率

        返回:
            估算股价
        """
        return eps * pe_ratio

    @staticmethod
    def pb_valuation(bvps: float, pb_ratio: float) -> float:
        """
        PB估值法

        参数:
            bvps: 每股净资产
            pb_ratio: 合理市净率

        返回:
            估算股价
        """
        return bvps * pb_ratio


class FinancialHealthScorer:
    """财务健康评分器"""

    @staticmethod
    def calculate_altman_z(total_assets: float, total_liabilities: float,
                          working_capital: float, retained_earnings: float,
                          ebit: float, market_cap: float, revenue: float) -> Dict:
        """
        Altman Z-Score 破产预警模型

        Z = 1.2*X1 + 1.4*X2 + 3.3*X3 + 0.6*X4 + 1.0*X5

        其中:
        X1 = 营运资本 / 总资产
        X2 = 留存收益 / 总资产
        X3 = EBIT / 总资产
        X4 = 股票市值 / 总负债
        X5 = 销售额 / 总资产

        判断标准:
        Z > 2.99: 安全区
        1.81 < Z < 2.99: 灰色区
        Z < 1.81: 危险区

        返回:
            包含Z值和判断结果的字典
        """
        # 计算五个变量
        x1 = working_capital / total_assets if total_assets > 0 else 0
        x2 = retained_earnings / total_assets if total_assets > 0 else 0
        x3 = ebit / total_assets if total_assets > 0 else 0
        x4 = market_cap / total_liabilities if total_liabilities > 0 else 0
        x5 = revenue / total_assets if total_assets > 0 else 0

        # 计算Z值
        z_score = 1.2 * x1 + 1.4 * x2 + 3.3 * x3 + 0.6 * x4 + 1.0 * x5

        # 判断风险区间
        if z_score > 2.99:
            risk_level = "安全区"
            risk_color = "绿色"
        elif z_score > 1.81:
            risk_level = "灰色区（需关注）"
            risk_color = "黄色"
        else:
            risk_level = "危险区"
            risk_color = "红色"

        return {
            'Z值': round(z_score, 3),
            '风险等级': risk_level,
            '风险颜色': risk_color,
            'X1_营运资本比': round(x1, 3),
            'X2_留存收益比': round(x2, 3),
            'X3_EBIT资产比': round(x3, 3),
            'X4_市值负债比': round(x4, 3),
            'X5_资产周转率': round(x5, 3)
        }


# ==================== 辅助函数 ====================

def interpret_pe(pe: float, industry_pe: float = None) -> str:
    """解读市盈率"""
    if pe <= 0:
        return "公司亏损或盈利为负，PE指标不适用"
    elif pe < 15:
        return "估值较低，可能被低估"
    elif pe < 25:
        return "估值合理"
    elif pe < 40:
        return "估值偏高"
    else:
        return "估值过高，需谨慎"

    if industry_pe:
        if pe < industry_pe * 0.8:
            return f"低于行业均值({industry_pe:.1f})，相对低估"
        elif pe > industry_pe * 1.2:
            return f"高于行业均值({industry_pe:.1f})，相对高估"


def interpret_roe(roe: float) -> str:
    """解读ROE"""
    if roe >= 20:
        return "ROE优秀，公司盈利能力极强"
    elif roe >= 15:
        return "ROE良好，公司盈利能力较强"
    elif roe >= 10:
        return "ROE一般，公司盈利能力尚可"
    elif roe >= 5:
        return "ROE偏低，公司盈利能力较弱"
    else:
        return "ROE很差，公司盈利能力堪忧"


def interpret_debt_ratio(ratio: float) -> str:
    """解读资产负债率"""
    if ratio < 40:
        return "负债率较低，财务风险小"
    elif ratio < 60:
        return "负债率适中，财务结构合理"
    elif ratio < 70:
        return "负债率偏高，需关注偿债能力"
    else:
        return "负债率过高，财务风险较大"


if __name__ == "__main__":
    # 测试杜邦分析
    print("=" * 60)
    print("杜邦分析测试 - 以模拟数据为例")
    print("=" * 60)

    result = DupontAnalysis.analyze(
        net_income=500,      # 净利润500万
        revenue=5000,        # 营业收入5000万
        total_assets=3000,   # 总资产3000万
        equity=1500          # 股东权益1500万
    )

    print("\n杜邦分析结果:")
    for k, v in result.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")

    # 测试Altman Z-Score
    print("\n" + "=" * 60)
    print("Altman Z-Score 破产预警测试")
    print("=" * 60)

    z_result = FinancialHealthScorer.calculate_altman_z(
        total_assets=10000,
        total_liabilities=4000,
        working_capital=2000,
        retained_earnings=3000,
        ebit=1500,
        market_cap=8000,
        revenue=8000
    )

    for k, v in z_result.items():
        print(f"  {k}: {v}")

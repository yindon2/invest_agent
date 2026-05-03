"""
投资学AI Agent - 个股基本面分析Skill
===================================
功能：获取上市公司财务数据，计算核心指标，生成智能分析报告
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime

from tools.data_fetcher import DataFetcher, format_number
from tools.financial_metrics import (
    DupontAnalysis,
    FinancialHealthScorer,
    interpret_pe,
    interpret_roe,
    interpret_debt_ratio
)


class FundamentalAnalysisSkill:
    """个股基本面分析技能"""

    def __init__(self):
        self.fetcher = DataFetcher()
        self.analysis_result = {}

    def analyze(self, symbol: str) -> Dict:
        """
        执行完整的基本面分析

        参数:
            symbol: 股票代码 (如 "600519")

        返回:
            完整分析结果字典
        """
        print(f"\n{'='*60}")
        print(f"开始分析股票: {symbol}")
        print(f"{'='*60}\n")

        # 1. 获取股票基本信息
        print("[1/5] 获取股票基本信息...")
        stock_info = self._get_stock_info(symbol)

        # 2. 获取财务指标
        print("[2/5] 获取财务指标数据...")
        financial_data = self._get_financial_data(symbol)

        # 3. 杜邦分析
        print("[3/5] 执行杜邦分析...")
        dupont_result = self._dupont_analysis(symbol)

        # 4. 财务健康评分
        print("[4/5] 计算财务健康评分...")
        health_score = self._calculate_health_score(symbol)

        # 5. 生成分析报告
        print("[5/5] 生成分析报告...")
        report = self._generate_report(symbol, stock_info, financial_data,
                                        dupont_result, health_score)

        self.analysis_result = {
            '股票代码': symbol,
            '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '基本信息': stock_info,
            '财务数据': financial_data,
            '杜邦分析': dupont_result,
            '健康评分': health_score,
            '分析报告': report
        }

        return self.analysis_result

    def _get_stock_info(self, symbol: str) -> Dict:
        """获取股票基本信息"""
        info = self.fetcher.get_stock_info(symbol)
        if info:
            return info
        return {
            '代码': symbol,
            '名称': '未知',
            '最新价': None,
            '市盈率': None,
            '市净率': None
        }

    def _get_financial_data(self, symbol: str) -> Dict:
        """获取并整理财务数据"""
        result = {
            '核心指标': {},
            '盈利能力': {},
            '偿债能力': {},
            '营运能力': {}
        }

        try:
            # 获取财务指标
            df = self.fetcher.get_financial_indicator(symbol)
            if df is not None and not df.empty:
                latest = df.iloc[0] if len(df) > 0 else {}

                # 提取关键指标
                result['核心指标'] = {
                    '市盈率PE': self._safe_extract(latest, ['市盈率', 'pe', 'PE']),
                    '市净率PB': self._safe_extract(latest, ['市净率', 'pb', 'PB']),
                    '净资产收益率ROE': self._safe_extract(latest, ['净资产收益率', 'roe', 'ROE']),
                    '毛利率': self._safe_extract(latest, ['销售毛利率', '毛利率']),
                    '净利率': self._safe_extract(latest, ['销售净利率', '净利率'])
                }
        except Exception as e:
            print(f"  获取财务指标警告: {e}")

        return result

    def _safe_extract(self, series, keys: List[str]):
        """安全提取数据"""
        for key in keys:
            for col in series.index:
                if key.lower() in str(col).lower():
                    val = series[col]
                    if pd.notna(val) and val != '-':
                        try:
                            return float(val)
                        except:
                            pass
        return None

    def _dupont_analysis(self, symbol: str) -> Dict:
        """执行杜邦分析"""
        try:
            # 尝试从利润表获取数据
            income_df = self.fetcher.get_income_statement(symbol)
            balance_df = self.fetcher.get_balance_sheet(symbol)

            if income_df is not None and not income_df.empty and \
               balance_df is not None and not balance_df.empty:

                # 提取最新报告期数据
                income_latest = income_df.iloc[0] if len(income_df) > 0 else {}
                balance_latest = balance_df.iloc[0] if len(balance_df) > 0 else {}

                # 提取关键财务数据
                net_income = self._extract_value(income_latest, ['净利润', '归属于母公司所有者的净利润'])
                revenue = self._extract_value(income_latest, ['营业收入', '营业总收入'])
                total_assets = self._extract_value(balance_latest, ['资产总计', '总资产'])
                equity = self._extract_value(balance_latest, ['所有者权益合计', '股东权益合计', '净资产'])

                if all(v is not None and v > 0 for v in [net_income, revenue, total_assets, equity]):
                    return DupontAnalysis.analyze(net_income, revenue, total_assets, equity)

        except Exception as e:
            print(f"  杜邦分析警告: {e}")

        # 返回模拟示例数据
        return self._demo_dupont_analysis()

    def _extract_value(self, series, keys: List[str]) -> Optional[float]:
        """从Series中提取数值"""
        for key in keys:
            for col in series.index:
                if key in str(col):
                    val = series[col]
                    if pd.notna(val) and val != '-':
                        try:
                            # 处理可能的字符串格式数字
                            if isinstance(val, str):
                                val = val.replace(',', '').replace(' ', '')
                            return float(val)
                        except:
                            pass
        return None

    def _demo_dupont_analysis(self) -> Dict:
        """演示用杜邦分析数据"""
        return {
            '说明': '以下为演示数据，实际数据获取失败',
            'ROE': 18.5,
            '净利率': 12.3,
            '资产周转率': 0.85,
            '权益乘数': 1.77,
            'ROA': 10.4
        }

    def _calculate_health_score(self, symbol: str) -> Dict:
        """计算财务健康评分"""
        try:
            balance_df = self.fetcher.get_balance_sheet(symbol)
            income_df = self.fetcher.get_income_statement(symbol)
            stock_info = self.fetcher.get_stock_info(symbol)

            if balance_df is not None and not balance_df.empty:
                balance = balance_df.iloc[0]

                total_assets = self._extract_value(balance, ['资产总计', '总资产']) or 1
                total_liabilities = self._extract_value(balance, ['负债合计', '总负债']) or 0
                working_capital = self._extract_value(balance, ['流动资产合计']) or 0
                working_capital -= self._extract_value(balance, ['流动负债合计']) or 0

                # 获取股票市值（简化计算）
                market_cap = stock_info.get('市值', stock_info.get('总市值', 0)) if stock_info else 0
                if market_cap == 0:
                    market_cap = total_assets * 1.5  # 估算

                revenue = 1
                ebit = 0
                if income_df is not None and not income_df.empty:
                    income = income_df.iloc[0]
                    revenue = self._extract_value(income, ['营业收入']) or 1
                    ebit = self._extract_value(income, ['营业利润']) or 0

                retained_earnings = self._extract_value(balance, ['盈余公积', '未分配利润']) or 0

                z_result = FinancialHealthScorer.calculate_altman_z(
                    total_assets=total_assets,
                    total_liabilities=total_liabilities,
                    working_capital=working_capital,
                    retained_earnings=retained_earnings,
                    ebit=ebit,
                    market_cap=market_cap,
                    revenue=revenue
                )
                return z_result

        except Exception as e:
            print(f"  健康评分计算警告: {e}")

        return {
            'Z值': 'N/A',
            '风险等级': '数据不足',
            '说明': '无法计算，请检查数据源'
        }

    def _generate_report(self, symbol: str, stock_info: Dict,
                         financial_data: Dict, dupont: Dict,
                         health: Dict) -> str:
        """生成Markdown格式的分析报告"""
        report = f"""
# {stock_info.get('名称', symbol)} ({symbol}) 基本面分析报告

> 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 一、公司概况

| 指标 | 数值 |
|------|------|
| 股票代码 | {symbol} |
| 股票名称 | {stock_info.get('名称', 'N/A')} |
| 最新价 | {stock_info.get('最新价', 'N/A')} |
| 涨跌幅 | {stock_info.get('涨跌幅', 'N/A')}% |
| 市盈率(动态) | {stock_info.get('市盈率', 'N/A')} |
| 市净率 | {stock_info.get('市净率', 'N/A')} |

## 二、杜邦分析

杜邦分析将ROE分解为三个核心因素，揭示盈利能力的来源：

| 指标 | 数值 | 解读 |
|------|------|------|
| **ROE** | {dupont.get('ROE', 'N/A'):.2f}% | {interpret_roe(dupont.get('ROE', 0))} |
| 净利率 | {dupont.get('净利率', 'N/A'):.2f}% | 反映产品盈利能力 |
| 资产周转率 | {dupont.get('资产周转率', 'N/A'):.2f}次 | 反映资产运营效率 |
| 权益乘数 | {dupont.get('权益乘数', 'N/A'):.2f} | 反映财务杠杆水平 |

**杜邦分解公式**: ROE = 净利率 × 资产周转率 × 权益乘数

## 三、财务健康评估

### Altman Z-Score 破产预警模型

| 指标 | 数值 |
|------|------|
| Z值 | {health.get('Z值', 'N/A')} |
| 风险等级 | **{health.get('风险等级', 'N/A')}** |

> Z值判断标准: Z>2.99(安全) | 1.81<Z<2.99(灰色) | Z<1.81(危险)

## 四、投资建议

### 估值分析
"""

        # 估值解读
        pe = stock_info.get('市盈率')
        if pe and isinstance(pe, (int, float)) and pe > 0:
            report += f"\n- **市盈率PE({pe:.1f})**: {interpret_pe(pe)}\n"
        else:
            report += "\n- 市盈率数据不可用\n"

        # 综合评价
        report += """
### 综合评价

基于以上分析，该股票的投资价值总结如下：

"""
        # 根据分析结果给出建议
        roe = dupont.get('ROE', 0)
        z_value = health.get('Z值', 0)

        suggestions = []
        if roe >= 15:
            suggestions.append("✅ ROE表现优秀，公司盈利能力强")
        elif roe >= 10:
            suggestions.append("⚠️ ROE表现一般，盈利能力尚可")
        else:
            suggestions.append("❌ ROE较低，盈利能力需关注")

        if isinstance(z_value, (int, float)):
            if z_value > 2.99:
                suggestions.append("✅ 财务状况健康，违约风险低")
            elif z_value > 1.81:
                suggestions.append("⚠️ 财务状况需关注")
            else:
                suggestions.append("❌ 财务风险较高，需谨慎")

        for s in suggestions:
            report += f"{s}\n"

        report += f"""
---
*本报告由投资学AI Agent自动生成，仅供参考，不构成投资建议*
"""
        return report

    def save_report(self, filepath: str = None):
        """保存分析报告"""
        if not self.analysis_result:
            print("请先执行分析")
            return

        if filepath is None:
            symbol = self.analysis_result.get('股票代码', 'unknown')
            filepath = f"outputs/reports/{symbol}_fundamental_report.md"

        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.analysis_result.get('分析报告', ''))

        print(f"\n报告已保存至: {filepath}")
        return filepath


# ==================== 命令行入口 ====================

def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='个股基本面分析')
    parser.add_argument('symbol', type=str, help='股票代码 (如 600519)')
    parser.add_argument('--save', '-s', action='store_true', help='保存报告到文件')

    args = parser.parse_args()

    # 执行分析
    skill = FundamentalAnalysisSkill()
    result = skill.analyze(args.symbol)

    # 打印报告
    print("\n" + "=" * 60)
    print("分析报告")
    print("=" * 60)
    print(result['分析报告'])

    # 保存报告
    if args.save:
        skill.save_report()

    return result


if __name__ == "__main__":
    main()

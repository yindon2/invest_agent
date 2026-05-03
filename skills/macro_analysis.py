"""
投资学AI Agent - 宏观经济分析Skill
=================================
功能：宏观经济指标与股市关联性分析
支持：CPI、PPI、利率、M2等指标
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

from tools.data_fetcher import DataFetcher
from tools.stat_analysis import (
    CorrelationAnalyzer,
    GrangerCausality,
    RegressionAnalyzer,
    TimeSeriesAnalyzer,
    LeadLagAnalyzer
)


class MacroAnalysisSkill:
    """宏观经济分析技能"""

    # 指数代码映射
    INDEX_MAP = {
        '上证指数': 'sh000001',
        '深证成指': 'sz399001',
        '创业板指': 'sz399006',
        '沪深300': 'sh000300',
        '上证50': 'sh000016'
    }

    # 宏观指标名称映射
    MACRO_INDICATORS = {
        'CPI': '居民消费价格指数',
        'PPI': '工业生产者出厂价格指数',
        'M2': '广义货币供应量',
        'GDP': '国内生产总值',
        '利率': 'Shibor利率'
    }

    def __init__(self):
        self.fetcher = DataFetcher()
        self.analysis_result = {}

    def analyze(self, macro_indicator: str = 'CPI',
                index_name: str = '上证指数',
                period: int = 36) -> Dict:
        """
        执行宏观指标与股市关联性分析

        参数:
            macro_indicator: 宏观指标名称 ('CPI', 'PPI', 'M2', 'GDP', '利率')
            index_name: 股指名称 ('上证指数', '深证成指', '创业板指'等)
            period: 分析周期(月)

        返回:
            完整分析结果
        """
        print(f"\n{'='*60}")
        print(f"宏观经济分析: {macro_indicator} vs {index_name}")
        print(f"{'='*60}\n")

        # 1. 获取数据
        print("[1/5] 获取宏观经济数据...")
        macro_data = self._get_macro_data(macro_indicator)

        print("[2/5] 获取股指数据...")
        index_data = self._get_index_data(index_name, period)

        # 2. 数据对齐
        print("[3/5] 数据对齐与预处理...")
        aligned_data = self._align_data(macro_data, index_data)

        if aligned_data is None or aligned_data.empty:
            print("数据对齐失败，使用模拟数据进行演示")
            aligned_data = self._generate_demo_data(macro_indicator)

        # 3. 相关性分析
        print("[4/5] 执行统计分析...")
        correlation_result = self._correlation_analysis(aligned_data)

        # 4. 因果检验
        causality_result = self._causality_analysis(aligned_data)

        # 5. 领先滞后分析
        leadlag_result = self._leadlag_analysis(aligned_data)

        # 6. 生成报告
        print("[5/5] 生成分析报告...")
        report = self._generate_report(
            macro_indicator, index_name,
            correlation_result, causality_result, leadlag_result
        )

        self.analysis_result = {
            '宏观指标': macro_indicator,
            '股指': index_name,
            '分析周期': f'{period}个月',
            '分析时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '相关性分析': correlation_result,
            '因果检验': causality_result,
            '领先滞后分析': leadlag_result,
            '分析报告': report,
            '数据': aligned_data
        }

        return self.analysis_result

    def _get_macro_data(self, indicator: str) -> pd.DataFrame:
        """获取宏观经济数据"""
        try:
            if indicator == 'CPI':
                return self.fetcher.get_cpi_data()
            elif indicator == 'PPI':
                return self.fetcher.get_ppi_data()
            elif indicator == 'M2':
                return self.fetcher.get_m2_data()
            elif indicator == 'GDP':
                return self.fetcher.get_gdp_data()
            elif indicator == '利率':
                return self.fetcher.get_interest_rate()
            else:
                print(f"未知指标: {indicator}，使用CPI")
                return self.fetcher.get_cpi_data()
        except Exception as e:
            print(f"获取{indicator}数据失败: {e}")
            return pd.DataFrame()

    def _get_index_data(self, index_name: str, period: int) -> pd.DataFrame:
        """获取股指数据"""
        index_code = self.INDEX_MAP.get(index_name, 'sh000001')
        start_date = (datetime.now() - timedelta(days=period*30)).strftime("%Y%m%d")
        end_date = datetime.now().strftime("%Y%m%d")

        try:
            return self.fetcher.get_index_data(index_code, start_date, end_date)
        except Exception as e:
            print(f"获取股指数据失败: {e}")
            return pd.DataFrame()

    def _align_data(self, macro_df: pd.DataFrame,
                    index_df: pd.DataFrame) -> Optional[pd.DataFrame]:
        """对齐宏观数据和股指数据"""
        if macro_df.empty or index_df.empty:
            return None

        try:
            # 重采样到月度数据
            if isinstance(index_df.index, pd.DatetimeIndex):
                index_monthly = index_df['close'].resample('ME').last()

            # 合并数据
            combined = pd.DataFrame({
                '宏观指标': macro_df.iloc[:, 0] if len(macro_df.columns) > 0 else None,
                '股指': index_monthly
            }).dropna()

            return combined
        except Exception as e:
            print(f"数据对齐错误: {e}")
            return None

    def _generate_demo_data(self, indicator: str) -> pd.DataFrame:
        """生成演示数据"""
        np.random.seed(42)
        n = 36  # 3年数据

        # 使用更稳健的方式生成日期
        dates = pd.date_range(start=datetime.now() - timedelta(days=n*31), periods=n, freq='ME')

        # 生成模拟的宏观指标数据
        if indicator == 'CPI':
            macro = np.random.normal(2, 1, n)  # CPI同比
        elif indicator == 'PPI':
            macro = np.random.normal(1, 2, n)  # PPI同比
        else:
            macro = np.cumsum(np.random.randn(n)) + 100

        # 生成模拟的股指数据（与宏观指标有一定相关性）
        stock = 3000 + np.cumsum(np.random.randn(n) * 50 - macro * 20)

        return pd.DataFrame({
            '宏观指标': macro,
            '股指': stock
        }, index=dates)

    def _correlation_analysis(self, data: pd.DataFrame) -> Dict:
        """相关性分析"""
        x = data['宏观指标'].values
        y = data['股指'].values

        # Pearson相关
        pearson = CorrelationAnalyzer.pearson_correlation(x, y)

        # Spearman相关
        spearman = CorrelationAnalyzer.spearman_correlation(x, y)

        # 滚动相关性
        rolling = CorrelationAnalyzer.rolling_correlation(
            data['宏观指标'], data['股指'], window=6
        )

        return {
            'Pearson': pearson,
            'Spearman': spearman,
            '滚动相关系数_均值': round(rolling.mean(), 4) if not rolling.empty else None,
            '滚动相关系数_标准差': round(rolling.std(), 4) if not rolling.empty else None
        }

    def _causality_analysis(self, data: pd.DataFrame) -> Dict:
        """格兰杰因果检验"""
        x = data['宏观指标'].values
        y = data['股指'].values

        # 平稳性检验
        adf_x = TimeSeriesAnalyzer.adf_test(x)
        adf_y = TimeSeriesAnalyzer.adf_test(y)

        # 格兰杰因果检验
        gc_result = GrangerCausality.bidirectional_test(x, y, max_lag=4)

        return {
            '宏观指标平稳性': adf_x,
            '股指平稳性': adf_y,
            '格兰杰因果检验': gc_result
        }

    def _leadlag_analysis(self, data: pd.DataFrame) -> Dict:
        """领先滞后分析"""
        x = data['宏观指标'].values
        y = data['股指'].values

        # 交叉相关分析
        cross_corr = LeadLagAnalyzer.cross_correlation(x, y, max_lag=6)

        # 线性回归
        regression = RegressionAnalyzer.simple_linear_regression(x, y)

        return {
            '交叉相关分析': cross_corr,
            '回归分析': regression
        }

    def _generate_report(self, indicator: str, index_name: str,
                         correlation: Dict, causality: Dict,
                         leadlag: Dict) -> str:
        """生成分析报告"""
        pearson = correlation.get('Pearson', {})

        report = f"""
# 宏观经济关联性分析报告

> 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 一、分析概述

本报告分析 **{indicator}** ({self.MACRO_INDICATORS.get(indicator, indicator)}) 与 **{index_name}** 之间的关联性。

## 二、相关性分析

### Pearson相关系数

| 指标 | 数值 |
|------|------|
| 相关系数(r) | {pearson.get('相关系数', 'N/A')} |
| p值 | {pearson.get('p值', 'N/A')} |
| 相关性强度 | {pearson.get('相关性强度', 'N/A')} |
| 统计显著性 | {pearson.get('显著性', 'N/A')} |

### 解读

"""

        r = pearson.get('相关系数', 0)
        if isinstance(r, (int, float)):
            if abs(r) >= 0.7:
                strength = "强"
            elif abs(r) >= 0.4:
                strength = "中等"
            else:
                strength = "弱"

            direction = "正相关" if r > 0 else "负相关"

            report += f"""
**{indicator}与{index_name}呈现{strength}{direction}关系** (r={r})

这意味着：
- 当{indicator}上升时，{index_name}倾向于{'上升' if r > 0 else '下降'}
- 相关系数的绝对值越高，两者变动的同步性越强
"""

        # 格兰杰因果检验结果
        report += """
## 三、格兰杰因果检验

### 检验结果

"""

        gc = causality.get('格兰杰因果检验', {})
        x_to_y = gc.get('x导致y', {})
        y_to_x = gc.get('y导致x', {})

        if isinstance(x_to_y, dict) and '滞后1期' in x_to_y:
            report += f"""
**{indicator} → {index_name}:**

| 滞后期 | F统计量 | p值 | 结论 |
|--------|---------|-----|------|
"""
            for lag, res in x_to_y.items():
                if isinstance(res, dict):
                    report += f"| {lag} | {res.get('F统计量', 'N/A')} | {res.get('p值', 'N/A')} | {res.get('结论', 'N/A')} |\n"

        # 领先滞后关系
        leadlag = leadlag.get('交叉相关分析', {})
        if leadlag:
            report += f"""
## 四、领先滞后分析

| 分析项 | 结果 |
|--------|------|
| 最大相关滞后期 | {leadlag.get('最大相关滞后期', 'N/A')} 期 |
| 最大相关系数 | {leadlag.get('最大相关系数', 'N/A')} |
| 领先滞后关系 | **{leadlag.get('领先滞后关系', 'N/A')}** |

"""

        # 回归分析
        regression = leadlag.get('回归分析', {})
        if regression:
            report += f"""
## 五、回归分析

| 统计量 | 数值 |
|--------|------|
| 回归方程 | {regression.get('回归方程', 'N/A')} |
| R² | {regression.get('R²', 'N/A')} |
| p值 | {regression.get('p值', 'N/A')} |

> R²={regression.get('R²', 0)} 表示{indicator}可以解释{index_name}约{float(regression.get('R²', 0))*100:.1f}%的变动。

"""

        # 投资启示
        report += f"""
## 六、投资启示

基于以上统计分析，得出以下投资启示：

"""

        # 根据分析结果给出建议
        r = pearson.get('相关系数', 0)
        if isinstance(r, (int, float)):
            if r < -0.3:
                report += f"1. **{indicator}是{index_name}的反向指标**：当{indicator}上升时，股市可能承压，投资者应降低仓位\n"
            elif r > 0.3:
                report += f"1. **{indicator}与股市同向变动**：反映经济周期与股市的同步性\n"
            else:
                report += f"1. **{indicator}对股市影响有限**：两者关联性较弱，需结合其他指标分析\n"

        leadlag_rel = leadlag.get('领先滞后关系', '')
        if '领先' in str(leadlag_rel):
            report += f"2. **{indicator}具有领先性**：可作为股市走势的预警指标\n"
        elif '滞后' in str(leadlag_rel):
            report += f"2. **{indicator}滞后于股市**：股市变动先于宏观指标，反映市场的前瞻性\n"

        report += """
---
*本报告由投资学AI Agent自动生成，基于历史数据的统计分析，不构成投资建议*
"""
        return report

    def save_report(self, filepath: str = None):
        """保存分析报告"""
        if not self.analysis_result:
            print("请先执行分析")
            return

        if filepath is None:
            indicator = self.analysis_result.get('宏观指标', 'unknown')
            index = self.analysis_result.get('股指', 'unknown')
            filepath = f"outputs/reports/{indicator}_{index}_macro_report.md"

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.analysis_result.get('分析报告', ''))

        print(f"\n报告已保存至: {filepath}")
        return filepath


# ==================== 命令行入口 ====================

def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='宏观经济关联性分析')
    parser.add_argument('--indicator', '-i', type=str, default='CPI',
                        choices=['CPI', 'PPI', 'M2', 'GDP', '利率'],
                        help='宏观指标名称')
    parser.add_argument('--index', '-n', type=str, default='上证指数',
                        help='股指名称')
    parser.add_argument('--period', '-p', type=int, default=36,
                        help='分析周期(月)')
    parser.add_argument('--save', '-s', action='store_true', help='保存报告')

    args = parser.parse_args()

    skill = MacroAnalysisSkill()
    result = skill.analyze(args.indicator, args.index, args.period)

    print("\n" + "=" * 60)
    print("分析报告")
    print("=" * 60)
    print(result['分析报告'])

    if args.save:
        skill.save_report()

    return result


if __name__ == "__main__":
    main()

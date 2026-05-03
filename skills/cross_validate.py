"""
投资学AI Agent - 交叉验证Skill (创新功能)
========================================
功能：多数据源交叉验证、异常检测、可信度评分
创新点：提升分析结论的可靠性
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from scipy import stats


class CrossValidationSkill:
    """
    交叉验证技能 - 创新功能

    核心思想：单一数据源可能存在误差或延迟，
    通过多维度交叉验证提升分析结论的可信度
    """

    def __init__(self):
        self.validation_results = {}

    def validate_financial_data(self, symbol: str,
                                 primary_data: Dict,
                                 secondary_sources: List[Dict] = None) -> Dict:
        """
        财务数据交叉验证

        参数:
            symbol: 股票代码
            primary_data: 主数据源数据
            secondary_sources: 辅助数据源列表

        返回:
            验证结果字典
        """
        print(f"\n{'='*50}")
        print(f"执行数据交叉验证: {symbol}")
        print(f"{'='*50}\n")

        results = {
            '股票代码': symbol,
            '验证时间': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            '指标验证': {},
            '整体可信度': 0,
            '异常标记': [],
            '建议': []
        }

        # 核心指标验证
        key_metrics = ['ROE', '毛利率', '净利率', '资产负债率', '市盈率', '市净率']

        for metric in key_metrics:
            primary_value = primary_data.get(metric)

            if primary_value is None:
                results['指标验证'][metric] = {
                    '状态': '缺失',
                    '可信度': 0
                }
                continue

            # 模拟多源验证（实际应用中从多个数据源获取）
            validation_result = self._validate_metric(
                metric, primary_value, secondary_sources
            )
            results['指标验证'][metric] = validation_result

            # 记录异常
            if validation_result['状态'] == '异常':
                results['异常标记'].append({
                    '指标': metric,
                    '原因': validation_result.get('异常原因', '未知')
                })

        # 计算整体可信度
        credibilities = [v['可信度'] for v in results['指标验证'].values()
                        if isinstance(v.get('可信度'), (int, float))]
        results['整体可信度'] = np.mean(credibilities) if credibilities else 0

        # 生成建议
        results['建议'] = self._generate_suggestions(results)

        self.validation_results = results
        return results

    def _validate_metric(self, metric: str, value: float,
                         secondary_sources: List[Dict] = None) -> Dict:
        """
        验证单个指标

        验证维度:
        1. 数值合理性检验（是否在正常范围内）
        2. 历史一致性检验（与历史数据是否矛盾）
        3. 行业对比检验（与行业均值差异是否合理）
        """
        result = {
            '原始值': value,
            '状态': '正常',
            '可信度': 100,
            '验证详情': {}
        }

        # 1. 数值合理性检验
        reasonableness = self._check_reasonableness(metric, value)
        result['验证详情']['合理性检验'] = reasonableness

        # 2. 模拟历史一致性检验
        consistency = self._check_consistency(metric, value)
        result['验证详情']['一致性检验'] = consistency

        # 3. 行业对比检验
        industry_cmp = self._check_industry_comparison(metric, value)
        result['验证详情']['行业对比'] = industry_cmp

        # 综合评估
        scores = [
            reasonableness.get('得分', 100),
            consistency.get('得分', 100),
            industry_cmp.get('得分', 100)
        ]
        result['可信度'] = np.mean(scores)

        # 判断状态
        if result['可信度'] < 50:
            result['状态'] = '异常'
            result['异常原因'] = '多项验证未通过'
        elif result['可信度'] < 70:
            result['状态'] = '存疑'
            result['异常原因'] = '部分验证存在偏差'

        return result

    def _check_reasonableness(self, metric: str, value: float) -> Dict:
        """
        数值合理性检验

        根据指标特性设置合理范围
        """
        # 定义各指标的合理范围
        reasonable_ranges = {
            'ROE': (-50, 100),           # ROE通常在-50%到100%
            '毛利率': (0, 100),          # 毛利率0-100%
            '净利率': (-50, 50),         # 净利率通常较低
            '资产负债率': (0, 100),      # 0-100%
            '市盈率': (0, 200),          # 通常0-200倍
            '市净率': (0, 20),           # 通常0-20倍
        }

        default_range = (-1e10, 1e10)
        min_val, max_val = reasonable_ranges.get(metric, default_range)

        if min_val <= value <= max_val:
            return {
                '状态': '通过',
                '说明': f'数值{value}在合理范围[{min_val}, {max_val}]内',
                '得分': 100
            }
        else:
            deviation = min(abs(value - min_val), abs(value - max_val))
            score = max(0, 100 - deviation * 2)
            return {
                '状态': '异常',
                '说明': f'数值{value}超出合理范围[{min_val}, {max_val}]',
                '偏离程度': deviation,
                '得分': score
            }

    def _check_consistency(self, metric: str, value: float) -> Dict:
        """
        历史一致性检验

        检验当前值与历史值的变化是否合理
        """
        # 模拟历史数据（实际应用中从数据库获取）
        historical_std = {
            'ROE': 5,
            '毛利率': 8,
            '净利率': 3,
            '资产负债率': 10,
            '市盈率': 20,
            '市净率': 2
        }

        historical_mean = {
            'ROE': 15,
            '毛利率': 35,
            '净利率': 10,
            '资产负债率': 45,
            '市盈率': 25,
            '市净率': 3
        }

        std = historical_std.get(metric, 10)
        mean = historical_mean.get(metric, value)

        # 计算偏离标准差的倍数
        z_score = abs(value - mean) / std if std > 0 else 0

        if z_score <= 2:
            return {
                '状态': '通过',
                '说明': f'与历史均值偏离{z_score:.1f}个标准差，变化合理',
                'Z-score': round(z_score, 2),
                '得分': 100
            }
        elif z_score <= 3:
            return {
                '状态': '注意',
                '说明': f'与历史均值偏离{z_score:.1f}个标准差，变化较大',
                'Z-score': round(z_score, 2),
                '得分': 70
            }
        else:
            return {
                '状态': '异常',
                '说明': f'与历史均值偏离{z_score:.1f}个标准差，变化异常',
                'Z-score': round(z_score, 2),
                '得分': 40
            }

    def _check_industry_comparison(self, metric: str, value: float) -> Dict:
        """
        行业对比检验

        与行业均值对比，检验是否偏离过大
        """
        # 模拟行业均值（实际应用中从行业数据库获取）
        industry_avg = {
            'ROE': 12,
            '毛利率': 30,
            '净利率': 8,
            '资产负债率': 50,
            '市盈率': 20,
            '市净率': 2.5
        }

        avg = industry_avg.get(metric, value)

        if avg == 0:
            return {'状态': '跳过', '说明': '行业均值不可用', '得分': 80}

        deviation_pct = abs(value - avg) / abs(avg) * 100

        if deviation_pct <= 30:
            return {
                '状态': '通过',
                '说明': f'与行业均值({avg})偏离{deviation_pct:.1f}%，属正常范围',
                '偏离百分比': round(deviation_pct, 2),
                '得分': 100
            }
        elif deviation_pct <= 50:
            return {
                '状态': '注意',
                '说明': f'与行业均值({avg})偏离{deviation_pct:.1f}%，需关注',
                '偏离百分比': round(deviation_pct, 2),
                '得分': 70
            }
        else:
            return {
                '状态': '异常',
                '说明': f'与行业均值({avg})偏离{deviation_pct:.1f}%，显著异常',
                '偏离百分比': round(deviation_pct, 2),
                '得分': 50
            }

    def _generate_suggestions(self, results: Dict) -> List[str]:
        """生成验证建议"""
        suggestions = []

        credibility = results['整体可信度']

        if credibility >= 90:
            suggestions.append("✅ 数据整体可信度高，可作为投资决策参考")
        elif credibility >= 70:
            suggestions.append("⚠️ 数据整体可信度良好，部分指标建议复核")
        elif credibility >= 50:
            suggestions.append("⚠️ 数据可信度一般，建议对比多个数据源")
        else:
            suggestions.append("❌ 数据可信度较低，强烈建议核实原始数据")

        # 针对异常指标的建议
        for anomaly in results['异常标记']:
            metric = anomaly['指标']
            reason = anomaly['原因']
            suggestions.append(f"📌 {metric}指标异常: {reason}，建议重点核实")

        return suggestions

    def generate_validation_report(self) -> str:
        """生成验证报告"""
        if not self.validation_results:
            return "尚未执行验证"

        r = self.validation_results
        report = f"""
# 数据交叉验证报告

> 验证时间: {r['验证时间']}
> 股票代码: {r['股票代码']}

## 一、整体评估

| 指标 | 结果 |
|------|------|
| 整体可信度 | **{r['整体可信度']:.1f}%** |
| 异常指标数 | {len(r['异常标记'])} |

## 二、各指标验证详情

| 指标 | 原始值 | 状态 | 可信度 |
|------|--------|------|--------|
"""

        for metric, detail in r['指标验证'].items():
            report += f"| {metric} | {detail.get('原始值', 'N/A')} | {detail.get('状态', 'N/A')} | {detail.get('可信度', 0):.0f}% |\n"

        report += """
## 三、验证建议

"""
        for suggestion in r['建议']:
            report += f"- {suggestion}\n"

        report += """
---
*本报告由投资学AI Agent交叉验证模块自动生成*
"""
        return report


class AnomalyDetector:
    """
    异常检测器

    使用统计方法检测财务数据中的异常值
    """

    @staticmethod
    def detect_outliers_zscore(data: np.ndarray, threshold: float = 3.0) -> Dict:
        """
        Z-score异常检测

        参数:
            data: 数据序列
            threshold: Z-score阈值

        返回:
            异常检测结果
        """
        mean = np.mean(data)
        std = np.std(data)

        z_scores = np.abs((data - mean) / std) if std > 0 else np.zeros_like(data)
        outliers = np.where(z_scores > threshold)[0]

        return {
            '异常值索引': outliers.tolist(),
            '异常值': data[outliers].tolist() if len(outliers) > 0 else [],
            '异常比例': len(outliers) / len(data) * 100,
            '阈值': threshold
        }

    @staticmethod
    def detect_outliers_iqr(data: np.ndarray, k: float = 1.5) -> Dict:
        """
        IQR（四分位距）异常检测

        参数:
            data: 数据序列
            k: IQR倍数

        返回:
            异常检测结果
        """
        q1 = np.percentile(data, 25)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        lower_bound = q1 - k * iqr
        upper_bound = q3 + k * iqr

        outliers = np.where((data < lower_bound) | (data > upper_bound))[0]

        return {
            '异常值索引': outliers.tolist(),
            '异常值': data[outliers].tolist() if len(outliers) > 0 else [],
            '下界': lower_bound,
            '上界': upper_bound,
            '异常比例': len(outliers) / len(data) * 100
        }

    @staticmethod
    def detect_trend_break(data: np.ndarray, window: int = 5) -> Dict:
        """
        趋势突变检测

        检测时间序列中的结构性变化点
        """
        n = len(data)
        breaks = []

        for i in range(window, n - window):
            before_mean = np.mean(data[i-window:i])
            after_mean = np.mean(data[i:i+window])

            # 检测均值突变
            if abs(after_mean - before_mean) > 2 * np.std(data):
                breaks.append(i)

        return {
            '突变点位置': breaks,
            '突变点数量': len(breaks),
            '检测窗口': window
        }


# ==================== 演示入口 ====================

def demo():
    """演示交叉验证功能"""
    print("=" * 60)
    print("投资学AI Agent - 交叉验证演示")
    print("=" * 60)

    # 模拟财务数据
    sample_data = {
        'ROE': 18.5,
        '毛利率': 45.2,
        '净利率': 12.3,
        '资产负债率': 35.0,
        '市盈率': 35.8,
        '市净率': 8.5
    }

    validator = CrossValidationSkill()
    result = validator.validate_financial_data('600519', sample_data)

    print("\n验证报告:")
    print(validator.generate_validation_report())

    # 演示异常检测
    print("\n" + "=" * 60)
    print("异常检测演示")
    print("=" * 60)

    data = np.array([10, 12, 11, 13, 10, 100, 11, 12, 10, 14])

    print("\n原始数据:", data)

    zscore_result = AnomalyDetector.detect_outliers_zscore(data)
    print(f"\nZ-score检测结果: 发现{len(zscore_result['异常值'])}个异常值")
    print(f"异常值: {zscore_result['异常值']}")

    iqr_result = AnomalyDetector.detect_outliers_iqr(data)
    print(f"\nIQR检测结果: 发现{len(iqr_result['异常值'])}个异常值")


if __name__ == "__main__":
    demo()

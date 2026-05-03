"""
投资学AI Agent - 统计分析工具模块
==============================
功能：相关性分析、因果检验、回归分析等统计方法
"""

import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import pearsonr, spearmanr, kendalltau
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class CorrelationAnalyzer:
    """相关性分析器"""

    @staticmethod
    def pearson_correlation(x: np.ndarray, y: np.ndarray) -> Dict:
        """
        Pearson相关系数分析

        参数:
            x: 变量1序列
            y: 变量2序列

        返回:
            包含相关系数、p值、解释的字典
        """
        corr, p_value = pearsonr(x, y)

        # 相关性强度解释
        abs_corr = abs(corr)
        if abs_corr >= 0.8:
            strength = "高度相关"
        elif abs_corr >= 0.5:
            strength = "中度相关"
        elif abs_corr >= 0.3:
            strength = "弱相关"
        else:
            strength = "几乎不相关"

        # 显著性判断
        significance = "显著" if p_value < 0.05 else "不显著"

        return {
            '相关系数': round(corr, 4),
            'p值': round(p_value, 6),
            '相关性强度': strength,
            '显著性': significance,
            '样本数': len(x)
        }

    @staticmethod
    def spearman_correlation(x: np.ndarray, y: np.ndarray) -> Dict:
        """
        Spearman秩相关系数分析

        适用场景：非线性关系、非正态分布数据
        """
        corr, p_value = spearmanr(x, y)

        return {
            'Spearman相关系数': round(corr, 4),
            'p值': round(p_value, 6),
            '显著性': "显著" if p_value < 0.05 else "不显著"
        }

    @staticmethod
    def rolling_correlation(x: pd.Series, y: pd.Series, window: int = 12) -> pd.Series:
        """
        滚动相关系数分析

        参数:
            x: 时间序列1
            y: 时间序列2
            window: 滚动窗口大小

        返回:
            滚动相关系数序列
        """
        # 对齐数据
        combined = pd.concat([x, y], axis=1).dropna()
        rolling_corr = combined.iloc[:, 0].rolling(window=window).corr(combined.iloc[:, 1])
        return rolling_corr

    @staticmethod
    def correlation_matrix(data: pd.DataFrame) -> pd.DataFrame:
        """
        计算相关系数矩阵

        参数:
            data: 多列数据的DataFrame

        返回:
            相关系数矩阵
        """
        return data.corr()


class GrangerCausality:
    """格兰杰因果检验"""

    @staticmethod
    def test(x: np.ndarray, y: np.ndarray, max_lag: int = 4) -> Dict:
        """
        格兰杰因果检验

        检验x是否格兰杰导致y

        参数:
            x: 原因变量序列
            y: 结果变量序列
            max_lag: 最大滞后阶数

        返回:
            包含各滞后阶数检验结果的字典
        """
        try:
            from statsmodels.tsa.stattools import grangercausalitytests

            # 准备数据
            data = np.column_stack([y, x])

            # 执行检验
            results = grangercausalitytests(data, maxlag=max_lag, verbose=False)

            # 整理结果
            output = {}
            for lag in range(1, max_lag + 1):
                f_test = results[lag][0]['ssr_ftest']
                output[f'滞后{lag}期'] = {
                    'F统计量': round(f_test[0], 4),
                    'p值': round(f_test[1], 6),
                    '结论': "存在格兰杰因果关系" if f_test[1] < 0.05 else "不存在格兰杰因果关系"
                }

            return output

        except ImportError:
            return {'error': '需要安装statsmodels库: pip install statsmodels'}
        except Exception as e:
            return {'error': str(e)}

    @staticmethod
    def bidirectional_test(x: np.ndarray, y: np.ndarray, max_lag: int = 4) -> Dict:
        """
        双向格兰杰因果检验

        同时检验x→y和y→x
        """
        result = {
            'x导致y': GrangerCausality.test(x, y, max_lag),
            'y导致x': GrangerCausality.test(y, x, max_lag)
        }
        return result


class RegressionAnalyzer:
    """回归分析器"""

    @staticmethod
    def simple_linear_regression(x: np.ndarray, y: np.ndarray) -> Dict:
        """
        简单线性回归

        y = α + βx + ε

        返回:
            回归系数、R²、t检验等统计量
        """
        from scipy import stats as sp_stats

        # 执行回归
        slope, intercept, r_value, p_value, std_err = sp_stats.linregress(x, y)

        # 计算R²
        r_squared = r_value ** 2

        # 计算残差
        y_pred = intercept + slope * x
        residuals = y - y_pred
        mse = np.mean(residuals ** 2)

        return {
            '截距(α)': round(intercept, 4),
            '斜率(β)': round(slope, 4),
            'R²': round(r_squared, 4),
            'p值': round(p_value, 6),
            '标准误': round(std_err, 4),
            'MSE': round(mse, 4),
            '回归方程': f'y = {intercept:.4f} + {slope:.4f}x'
        }

    @staticmethod
    def multiple_regression(X: np.ndarray, y: np.ndarray, feature_names: List[str] = None) -> Dict:
        """
        多元线性回归

        y = β₀ + β₁x₁ + β₂x₂ + ... + βₙxₙ + ε
        """
        try:
            import statsmodels.api as sm

            # 添加常数项
            X_with_const = sm.add_constant(X)

            # 执行回归
            model = sm.OLS(y, X_with_const).fit()

            # 整理系数
            coef_names = ['截距'] + (feature_names or [f'x{i+1}' for i in range(X.shape[1])])
            coefficients = dict(zip(coef_names, model.params.round(4)))

            return {
                '系数': coefficients,
                'R²': round(model.rsquared, 4),
                '调整R²': round(model.rsquared_adj, 4),
                'F统计量': round(model.fvalue, 4),
                'F检验p值': round(model.f_pvalue, 6),
                'AIC': round(model.aic, 2),
                'BIC': round(model.bic, 2),
                '摘要': model.summary().as_text()
            }

        except ImportError:
            return {'error': '需要安装statsmodels库: pip install statsmodels'}


class TimeSeriesAnalyzer:
    """时间序列分析器"""

    @staticmethod
    def adf_test(series: np.ndarray) -> Dict:
        """
        ADF单位根检验（平稳性检验）

        原假设：序列存在单位根（非平稳）
        备择假设：序列不存在单位根（平稳）

        返回:
            检验统计量、p值、是否平稳
        """
        try:
            from statsmodels.tsa.stattools import adfuller

            result = adfuller(series, autolag='AIC')

            return {
                'ADF统计量': round(result[0], 4),
                'p值': round(result[1], 6),
                '滞后阶数': result[2],
                '观测数': result[3],
                '结论': "平稳序列" if result[1] < 0.05 else "非平稳序列",
                '临界值': {k: round(v, 4) for k, v in result[4].items()}
            }

        except ImportError:
            return {'error': '需要安装statsmodels库'}

    @staticmethod
    def kpss_test(series: np.ndarray) -> Dict:
        """
        KPSS检验（平稳性检验）

        原假设：序列是平稳的
        备择假设：序列是非平稳的
        """
        try:
            from statsmodels.tsa.stattools import kpss

            statistic, p_value, n_lags, critical_values = kpss(series, regression='c')

            return {
                'KPSS统计量': round(statistic, 4),
                'p值': round(p_value, 6),
                '滞后阶数': n_lags,
                '结论': "非平稳序列" if p_value < 0.05 else "平稳序列"
            }

        except ImportError:
            return {'error': '需要安装statsmodels库'}

    @staticmethod
    def calculate_returns(prices: np.ndarray, method: str = 'simple') -> np.ndarray:
        """
        计算收益率

        参数:
            prices: 价格序列
            method: 'simple' (简单收益率) 或 'log' (对数收益率)

        返回:
            收益率序列
        """
        prices = np.array(prices)
        if method == 'simple':
            returns = np.diff(prices) / prices[:-1]
        else:  # log
            returns = np.diff(np.log(prices))
        return returns

    @staticmethod
    def calculate_volatility(returns: np.ndarray, annualize: bool = True) -> float:
        """
        计算波动率

        参数:
            returns: 收益率序列
            annualize: 是否年化

        返回:
            波动率
        """
        vol = np.std(returns, ddof=1)
        if annualize:
            vol = vol * np.sqrt(252)  # 假设252个交易日
        return vol


class LeadLagAnalyzer:
    """领先滞后关系分析器"""

    @staticmethod
    def cross_correlation(x: np.ndarray, y: np.ndarray, max_lag: int = 12) -> Dict:
        """
        交叉相关分析

        分析x和y之间的领先/滞后关系

        参数:
            x: 序列1
            y: 序列2
            max_lag: 最大滞后/领先期数

        返回:
            各滞后期的相关系数
        """
        # 标准化
        x = (x - np.mean(x)) / np.std(x)
        y = (y - np.mean(y)) / np.std(y)

        n = len(x)
        correlations = {}

        # 计算各滞后期的相关系数
        for lag in range(-max_lag, max_lag + 1):
            if lag < 0:
                corr = np.corrcoef(x[:lag], y[-lag:])[0, 1]
            elif lag > 0:
                corr = np.corrcoef(x[lag:], y[:-lag])[0, 1]
            else:
                corr = np.corrcoef(x, y)[0, 1]

            correlations[lag] = round(corr, 4)

        # 找出最大相关系数对应的滞后期
        max_lag_corr = max(correlations.items(), key=lambda x: abs(x[1]))

        # 判断领先滞后关系
        if max_lag_corr[0] > 0:
            relationship = f"x领先y {max_lag_corr[0]} 期"
        elif max_lag_corr[0] < 0:
            relationship = f"x滞后y {abs(max_lag_corr[0])} 期"
        else:
            relationship = "x和y同步"

        return {
            '各期相关系数': correlations,
            '最大相关滞后期': max_lag_corr[0],
            '最大相关系数': max_lag_corr[1],
            '领先滞后关系': relationship
        }


# ==================== 工具函数 ====================

def normalize_series(series: np.ndarray) -> np.ndarray:
    """标准化序列（Z-score标准化）"""
    return (series - np.mean(series)) / np.std(series)


def minmax_scale(series: np.ndarray) -> np.ndarray:
    """Min-Max归一化到[0,1]"""
    return (series - np.min(series)) / (np.max(series) - np.min(series))


def calculate_drawdown(prices: np.ndarray) -> Dict:
    """计算最大回撤"""
    cumulative = np.maximum.accumulate(prices)
    drawdown = (prices - cumulative) / cumulative
    max_drawdown = np.min(drawdown)

    return {
        '最大回撤': round(max_drawdown, 4),
        '最大回撤百分比': f"{max_drawdown * 100:.2f}%"
    }


if __name__ == "__main__":
    # 测试相关性分析
    print("=" * 60)
    print("相关性分析测试")
    print("=" * 60)

    np.random.seed(42)
    x = np.random.randn(100)
    y = x * 0.8 + np.random.randn(100) * 0.3

    result = CorrelationAnalyzer.pearson_correlation(x, y)
    for k, v in result.items():
        print(f"  {k}: {v}")

    # 测试格兰杰因果检验
    print("\n" + "=" * 60)
    print("格兰杰因果检验测试")
    print("=" * 60)

    # 生成测试数据（x领先y）
    n = 100
    x = np.random.randn(n)
    y = np.zeros(n)
    for i in range(2, n):
        y[i] = 0.5 * x[i-1] + 0.3 * x[i-2] + np.random.randn() * 0.1

    gc_result = GrangerCausality.test(x, y, max_lag=4)
    for lag, res in gc_result.items():
        print(f"\n{lag}:")
        for k, v in res.items():
            print(f"  {k}: {v}")

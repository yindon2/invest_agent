"""
投资学AI Agent - 可视化输出Skill
===============================
功能：生成各类金融分析图表
支持：雷达图、趋势图、热力图、杜邦分析图等
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from typing import Dict, List, Optional, Tuple
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


class VisualizationSkill:
    """可视化技能"""

    def __init__(self, output_dir: str = "outputs/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def plot_financial_radar(self, metrics: Dict, title: str = "财务指标雷达图",
                             save_path: str = None) -> str:
        """
        绘制财务指标雷达图

        参数:
            metrics: 指标字典 {指标名: 数值}
            title: 图表标题
            save_path: 保存路径

        返回:
            图片保存路径
        """
        # 准备数据
        labels = list(metrics.keys())
        values = list(metrics.values())
        num_vars = len(labels)

        # 计算角度
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        values += values[:1]  # 闭合
        angles += angles[:1]

        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 8), subplot_kw=dict(polar=True))

        # 绘制雷达图
        ax.fill(angles, values, color='steelblue', alpha=0.25)
        ax.plot(angles, values, color='steelblue', linewidth=2, marker='o', markersize=6)

        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(labels, fontsize=12)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # 保存图表
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"雷达图已保存: {save_path}")
        return save_path

    def plot_time_series(self, data: pd.DataFrame, columns: List[str] = None,
                         title: str = "时间序列图", ylabel: str = "数值",
                         save_path: str = None) -> str:
        """
        绘制时间序列图

        参数:
            data: 时间序列DataFrame (索引为日期)
            columns: 要绘制的列名列表
            title: 图表标题
            ylabel: Y轴标签
            save_path: 保存路径

        返回:
            图片保存路径
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        if columns is None:
            columns = data.columns.tolist()

        colors = plt.cm.Set2(np.linspace(0, 1, len(columns)))

        for col, color in zip(columns, colors):
            ax.plot(data.index, data[col], label=col, color=color, linewidth=1.5)

        ax.set_xlabel('日期', fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        # 格式化x轴日期
        fig.autofmt_xdate()

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"timeseries_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"时间序列图已保存: {save_path}")
        return save_path

    def plot_correlation_heatmap(self, corr_matrix: pd.DataFrame,
                                  title: str = "相关性热力图",
                                  save_path: str = None) -> str:
        """
        绘制相关性热力图

        参数:
            corr_matrix: 相关系数矩阵
            title: 图表标题
            save_path: 保存路径

        返回:
            图片保存路径
        """
        fig, ax = plt.subplots(figsize=(10, 8))

        # 绘制热力图
        im = ax.imshow(corr_matrix, cmap='RdBu_r', aspect='auto', vmin=-1, vmax=1)

        # 设置刻度
        ax.set_xticks(np.arange(len(corr_matrix.columns)))
        ax.set_yticks(np.arange(len(corr_matrix.index)))
        ax.set_xticklabels(corr_matrix.columns, fontsize=10)
        ax.set_yticklabels(corr_matrix.index, fontsize=10)

        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

        # 添加数值标签
        for i in range(len(corr_matrix.index)):
            for j in range(len(corr_matrix.columns)):
                value = corr_matrix.iloc[i, j]
                color = 'white' if abs(value) > 0.5 else 'black'
                ax.text(j, i, f'{value:.2f}', ha='center', va='center', color=color, fontsize=9)

        ax.set_title(title, fontsize=14, fontweight='bold')

        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax, shrink=0.8)
        cbar.set_label('相关系数', fontsize=11)

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"热力图已保存: {save_path}")
        return save_path

    def plot_dupont_analysis(self, dupont_data: Dict,
                             title: str = "杜邦分析图",
                             save_path: str = None) -> str:
        """
        绘制杜邦分析分解图

        参数:
            dupont_data: 杜邦分析结果字典
            title: 图表标题
            save_path: 保存路径

        返回:
            图片保存路径
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 8)
        ax.axis('off')

        # 定义节点位置和大小
        def draw_box(x, y, width, height, text, value, color='lightblue', fontsize=10):
            box = FancyBboxPatch((x - width/2, y - height/2), width, height,
                                  boxstyle="round,pad=0.05,rounding_size=0.2",
                                  facecolor=color, edgecolor='black', linewidth=1.5)
            ax.add_patch(box)
            ax.text(x, y + 0.2, text, ha='center', va='center', fontsize=fontsize, fontweight='bold')
            if value is not None:
                ax.text(x, y - 0.25, f'{value:.2f}%' if isinstance(value, float) and abs(value) < 10 else f'{value:.2f}',
                       ha='center', va='center', fontsize=fontsize-1, color='darkblue')

        # 绘制ROE (顶层)
        draw_box(7, 7, 2.5, 1, 'ROE', dupont_data.get('ROE'), 'gold', 12)

        # 绘制第二层
        draw_box(3, 5, 2.2, 1, '净利率', dupont_data.get('净利率'), 'lightcoral')
        draw_box(7, 5, 2.5, 1, '资产周转率', dupont_data.get('资产周转率'), 'lightgreen')
        draw_box(11, 5, 2.2, 1, '权益乘数', dupont_data.get('权益乘数'), 'lightyellow')

        # 绘制连接线
        line_style = dict(arrowstyle='->', color='gray', lw=2)

        # ROE 到 三个分解因素
        ax.annotate('', xy=(3, 5.5), xytext=(5.5, 6.5), arrowprops=line_style)
        ax.annotate('', xy=(7, 5.5), xytext=(7, 6.5), arrowprops=line_style)
        ax.annotate('', xy=(11, 5.5), xytext=(8.5, 6.5), arrowprops=line_style)

        # 添加公式说明
        ax.text(7, 3.5, 'ROE = 净利率 × 资产周转率 × 权益乘数',
               ha='center', va='center', fontsize=12, style='italic',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # 添加解释说明
        explanations = [
            ('净利率', '反映盈利能力', 3, 3),
            ('资产周转率', '反映营运效率', 7, 3),
            ('权益乘数', '反映财务杠杆', 11, 3)
        ]

        for name, desc, x, y in explanations:
            ax.text(x, y, desc, ha='center', va='center', fontsize=9, color='gray')

        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"dupont_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"杜邦分析图已保存: {save_path}")
        return save_path

    def plot_health_gauge(self, z_score: float, title: str = "财务健康评分",
                          save_path: str = None) -> str:
        """
        绘制财务健康仪表盘

        参数:
            z_score: Altman Z值
            title: 图表标题
            save_path: 保存路径

        返回:
            图片保存路径
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        # 绘制仪表盘背景
        theta = np.linspace(0, np.pi, 100)

        # 安全区 (绿色)
        theta_safe = np.linspace(0, np.pi/3, 30)
        ax.fill_between(theta_safe, 0, 1, color='green', alpha=0.3)

        # 灰色区 (黄色)
        theta_gray = np.linspace(np.pi/3, 2*np.pi/3, 30)
        ax.fill_between(theta_gray, 0, 1, color='yellow', alpha=0.3)

        # 危险区 (红色)
        theta_danger = np.linspace(2*np.pi/3, np.pi, 30)
        ax.fill_between(theta_danger, 0, 1, color='red', alpha=0.3)

        # 绘制指针
        # 将Z值映射到角度 (假设Z范围0-5)
        z_clamped = max(0, min(z_score, 5))
        pointer_angle = np.pi * (1 - z_clamped / 5)

        ax.arrow(np.pi/2, 0.3, 0.5*np.cos(pointer_angle), 0.5*np.sin(pointer_angle),
                head_width=0.05, head_length=0.05, fc='black', ec='black')

        # 添加标签
        ax.text(np.pi/6, -0.15, '危险\n(Z<1.81)', ha='center', fontsize=10, color='red')
        ax.text(np.pi/2, -0.15, '灰色\n(1.81<Z<2.99)', ha='center', fontsize=10, color='orange')
        ax.text(5*np.pi/6, -0.15, '安全\n(Z>2.99)', ha='center', fontsize=10, color='green')

        # 显示Z值
        ax.text(np.pi/2, 0.8, f'Z = {z_score:.2f}', ha='center', fontsize=16, fontweight='bold')

        ax.set_xlim(-0.2, np.pi + 0.2)
        ax.set_ylim(-0.3, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold')

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"health_gauge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"健康仪表盘已保存: {save_path}")
        return save_path

    def plot_macro_correlation(self, macro_data: pd.Series, stock_data: pd.Series,
                               title: str = "宏观指标与股指对比",
                               save_path: str = None) -> str:
        """
        绘制宏观指标与股指对比图（双Y轴）

        参数:
            macro_data: 宏观指标序列
            stock_data: 股指数据序列
            title: 图表标题
            save_path: 保存路径

        返回:
            图片保存路径
        """
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # 对齐数据
        combined = pd.concat([macro_data, stock_data], axis=1).dropna()
        combined.columns = ['宏观指标', '股指']

        # 左Y轴 - 宏观指标
        color1 = 'tab:blue'
        ax1.set_xlabel('日期', fontsize=11)
        ax1.set_ylabel('宏观指标', color=color1, fontsize=11)
        ax1.plot(combined.index, combined['宏观指标'], color=color1, linewidth=1.5, label='宏观指标')
        ax1.tick_params(axis='y', labelcolor=color1)

        # 右Y轴 - 股指
        ax2 = ax1.twinx()
        color2 = 'tab:red'
        ax2.set_ylabel('股指', color=color2, fontsize=11)
        ax2.plot(combined.index, combined['股指'], color=color2, linewidth=1.5, label='股指')
        ax2.tick_params(axis='y', labelcolor=color2)

        # 添加图例
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        ax1.set_title(title, fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        fig.autofmt_xdate()

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"macro_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"宏观对比图已保存: {save_path}")
        return save_path

    def plot_rolling_correlation(self, rolling_corr: pd.Series,
                                 title: str = "滚动相关系数",
                                 save_path: str = None) -> str:
        """
        绘制滚动相关系数图

        参数:
            rolling_corr: 滚动相关系数序列
            title: 图表标题
            save_path: 保存路径

        返回:
            图片保存路径
        """
        fig, ax = plt.subplots(figsize=(12, 5))

        ax.plot(rolling_corr.index, rolling_corr, color='steelblue', linewidth=1.5)
        ax.axhline(y=0, color='gray', linestyle='--', linewidth=1)
        ax.axhline(y=0.5, color='green', linestyle=':', linewidth=1, alpha=0.7)
        ax.axhline(y=-0.5, color='red', linestyle=':', linewidth=1, alpha=0.7)

        ax.fill_between(rolling_corr.index, rolling_corr, 0,
                        where=rolling_corr > 0, color='green', alpha=0.3)
        ax.fill_between(rolling_corr.index, rolling_corr, 0,
                        where=rolling_corr < 0, color='red', alpha=0.3)

        ax.set_xlabel('日期', fontsize=11)
        ax.set_ylabel('相关系数', fontsize=11)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_ylim(-1, 1)
        ax.grid(True, alpha=0.3)

        fig.autofmt_xdate()

        if save_path is None:
            save_path = os.path.join(self.output_dir, f"rolling_corr_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")

        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        print(f"滚动相关系数图已保存: {save_path}")
        return save_path


# ==================== 演示入口 ====================

def demo():
    """演示可视化功能"""
    viz = VisualizationSkill()

    print("=" * 60)
    print("投资学AI Agent - 可视化演示")
    print("=" * 60)

    # 1. 雷达图
    print("\n[1] 生成财务指标雷达图...")
    metrics = {
        'ROE': 18.5,
        '毛利率': 45.2,
        '净利率': 12.3,
        '资产周转率': 85,
        '负债率': 35
    }
    viz.plot_financial_radar(metrics, "贵州茅台财务指标雷达图")

    # 2. 杜邦分析图
    print("\n[2] 生成杜邦分析图...")
    dupont = {
        'ROE': 18.5,
        '净利率': 12.3,
        '资产周转率': 0.85,
        '权益乘数': 1.77
    }
    viz.plot_dupont_analysis(dupont, "贵州茅台杜邦分析")

    # 3. 健康仪表盘
    print("\n[3] 生成财务健康仪表盘...")
    viz.plot_health_gauge(3.25, "贵州茅台财务健康评分")

    # 4. 时间序列图
    print("\n[4] 生成时间序列图...")
    dates = pd.date_range(end=datetime.now(), periods=36, freq='ME')
    data = pd.DataFrame({
        '上证指数': 3000 + np.cumsum(np.random.randn(36) * 50),
        '深证成指': 10000 + np.cumsum(np.random.randn(36) * 100)
    }, index=dates)
    viz.plot_time_series(data, title="股指走势对比")

    # 5. 相关性热力图
    print("\n[5] 生成相关性热力图...")
    corr_data = pd.DataFrame({
        'CPI': np.random.randn(36),
        'PPI': np.random.randn(36) * 0.8 + np.random.randn(36) * 0.2,
        '上证指数': np.random.randn(36) * 0.3 - np.random.randn(36) * 0.7,
    }).corr()
    viz.plot_correlation_heatmap(corr_data, "宏观指标与股指相关性")

    print("\n" + "=" * 60)
    print("演示完成！图表已保存至 outputs/charts/ 目录")
    print("=" * 60)


if __name__ == "__main__":
    demo()

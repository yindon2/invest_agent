"""
投资学AI Agent - 主程序入口
==========================
功能：整合所有分析技能，提供统一的调用接口
支持：个股基本面分析、宏观经济分析、可视化输出、交叉验证

使用方法:
    python agent.py fundamental <股票代码>          # 个股基本面分析
    python agent.py macro --indicator CPI --index 上证指数  # 宏观经济分析
    python agent.py demo                            # 运行演示
"""

import sys
import os
import argparse
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills.fundamental import FundamentalAnalysisSkill
from skills.macro_analysis import MacroAnalysisSkill
from skills.visualization import VisualizationSkill
from skills.cross_validate import CrossValidationSkill


class InvestmentAgent:
    """
    投资学AI Agent主类

    整合四大核心技能:
    1. FundamentalAnalysisSkill - 个股基本面分析
    2. MacroAnalysisSkill - 宏观经济关联性分析
    3. VisualizationSkill - 可视化输出
    4. CrossValidationSkill - 交叉验证（创新功能）
    """

    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
        os.makedirs(f"{output_dir}/charts", exist_ok=True)

        # 初始化各技能模块
        self.fundamental = FundamentalAnalysisSkill()
        self.macro = MacroAnalysisSkill()
        self.viz = VisualizationSkill(f"{output_dir}/charts")
        self.validator = CrossValidationSkill()

    def analyze_stock(self, symbol: str, enable_validation: bool = True) -> dict:
        """
        执行完整的个股分析

        参数:
            symbol: 股票代码 (如 "600519")
            enable_validation: 是否启用交叉验证

        返回:
            完整分析结果
        """
        print("\n" + "=" * 60)
        print(f"投资学AI Agent - 个股分析")
        print(f"目标: {symbol}")
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

        # 1. 基本面分析
        print("\n[Step 1/4] 执行基本面分析...")
        fundamental_result = self.fundamental.analyze(symbol)

        # 2. 交叉验证（创新功能）
        if enable_validation:
            print("\n[Step 2/4] 执行数据交叉验证...")
            financial_data = fundamental_result.get('财务数据', {}).get('核心指标', {})
            validation_result = self.validator.validate_financial_data(
                symbol, financial_data
            )
            fundamental_result['交叉验证'] = validation_result
        else:
            print("\n[Step 2/4] 跳过交叉验证")
            fundamental_result['交叉验证'] = None

        # 3. 生成可视化图表
        print("\n[Step 3/4] 生成可视化图表...")
        charts = self._generate_stock_charts(fundamental_result)
        fundamental_result['图表'] = charts

        # 4. 保存报告
        print("\n[Step 4/4] 保存分析报告...")
        report_path = self.fundamental.save_report()
        fundamental_result['报告路径'] = report_path

        # 打印摘要
        self._print_summary(fundamental_result)

        return fundamental_result

    def analyze_macro(self, indicator: str = 'CPI',
                      index_name: str = '上证指数',
                      period: int = 36) -> dict:
        """
        执行宏观经济关联性分析

        参数:
            indicator: 宏观指标 ('CPI', 'PPI', 'M2', 'GDP', '利率')
            index_name: 股指名称
            period: 分析周期(月)

        返回:
            完整分析结果
        """
        print("\n" + "=" * 60)
        print(f"投资学AI Agent - 宏观经济分析")
        print(f"指标: {indicator} vs {index_name}")
        print(f"周期: {period}个月")
        print("=" * 60)

        # 1. 执行宏观分析
        print("\n[Step 1/3] 执行关联性分析...")
        macro_result = self.macro.analyze(indicator, index_name, period)

        # 2. 生成可视化
        print("\n[Step 2/3] 生成可视化图表...")
        charts = self._generate_macro_charts(macro_result)
        macro_result['图表'] = charts

        # 3. 保存报告
        print("\n[Step 3/3] 保存分析报告...")
        report_path = self.macro.save_report()
        macro_result['报告路径'] = report_path

        return macro_result

    def _generate_stock_charts(self, result: dict) -> dict:
        """生成个股分析图表"""
        charts = {}

        # 杜邦分析图
        dupont_data = result.get('杜邦分析', {})
        if dupont_data:
            path = self.viz.plot_dupont_analysis(
                dupont_data,
                title=f"{result.get('股票代码', '')} 杜邦分析"
            )
            charts['杜邦分析图'] = path

        # 健康仪表盘
        health = result.get('健康评分', {})
        z_value = health.get('Z值', 0)
        if isinstance(z_value, (int, float)):
            path = self.viz.plot_health_gauge(
                z_value,
                title=f"{result.get('股票代码', '')} 财务健康评分"
            )
            charts['健康仪表盘'] = path

        # 财务指标雷达图
        metrics = result.get('财务数据', {}).get('核心指标', {})
        if metrics:
            # 过滤有效数据
            valid_metrics = {k: v for k, v in metrics.items()
                           if isinstance(v, (int, float)) and v is not None}
            if valid_metrics:
                path = self.viz.plot_financial_radar(
                    valid_metrics,
                    title=f"{result.get('股票代码', '')} 财务指标"
                )
                charts['雷达图'] = path

        return charts

    def _generate_macro_charts(self, result: dict) -> dict:
        """生成宏观分析图表"""
        charts = {}

        data = result.get('数据')
        if data is not None and not data.empty:
            # 宏观指标与股指对比图
            path = self.viz.plot_macro_correlation(
                data['宏观指标'],
                data['股指'],
                title=f"{result.get('宏观指标', '')} vs {result.get('股指', '')}"
            )
            charts['对比图'] = path

            # 滚动相关系数图
            from tools.stat_analysis import CorrelationAnalyzer
            rolling = CorrelationAnalyzer.rolling_correlation(
                data['宏观指标'], data['股指'], window=6
            )
            if not rolling.empty:
                path = self.viz.plot_rolling_correlation(
                    rolling,
                    title=f"{result.get('宏观指标', '')}与{result.get('股指', '')}滚动相关系数"
                )
                charts['滚动相关系数图'] = path

        return charts

    def _print_summary(self, result: dict):
        """打印分析摘要"""
        print("\n" + "=" * 60)
        print("分析摘要")
        print("=" * 60)

        # 基本信息
        info = result.get('基本信息', {})
        print(f"\n股票: {info.get('名称', 'N/A')} ({info.get('代码', 'N/A')})")
        print(f"最新价: {info.get('最新价', 'N/A')}")

        # 杜邦分析
        dupont = result.get('杜邦分析', {})
        print(f"\n杜邦分析:")
        print(f"  ROE: {dupont.get('ROE', 'N/A')}%")
        print(f"  净利率: {dupont.get('净利率', 'N/A')}%")
        print(f"  资产周转率: {dupont.get('资产周转率', 'N/A')}")

        # 健康评分
        health = result.get('健康评分', {})
        print(f"\n财务健康:")
        print(f"  Z值: {health.get('Z值', 'N/A')}")
        print(f"  风险等级: {health.get('风险等级', 'N/A')}")

        # 交叉验证
        validation = result.get('交叉验证')
        if validation:
            print(f"\n数据可信度: {validation.get('整体可信度', 0):.1f}%")

        # 图表
        charts = result.get('图表', {})
        if charts:
            print(f"\n生成图表:")
            for name, path in charts.items():
                print(f"  - {name}: {path}")

        print(f"\n报告已保存: {result.get('报告路径', 'N/A')}")
        print("=" * 60)


def demo():
    """运行演示"""
    print("\n" + "=" * 70)
    print("    投资学AI Agent 演示")
    print("    基于Claude Code Agent能力框架")
    print("=" * 70)

    agent = InvestmentAgent()

    # 演示1: 个股基本面分析
    print("\n\n" + "-" * 70)
    print("演示1: 个股基本面分析 (以贵州茅台 600519 为例)")
    print("-" * 70)

    result = agent.analyze_stock("600519", enable_validation=True)

    # 演示2: 宏观经济分析
    print("\n\n" + "-" * 70)
    print("演示2: 宏观经济关联性分析 (CPI vs 上证指数)")
    print("-" * 70)

    macro_result = agent.analyze_macro('CPI', '上证指数', period=24)

    print("\n\n" + "=" * 70)
    print("演示完成!")
    print("所有报告和图表已保存至 outputs/ 目录")
    print("=" * 70)

    return result, macro_result


def main():
    """命令行主入口"""
    parser = argparse.ArgumentParser(
        description='投资学AI Agent - 基于Claude Code Agent能力框架',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python agent.py fundamental 600519           # 分析贵州茅台
  python agent.py fundamental 000001 --save    # 分析平安银行并保存报告
  python agent.py macro -i CPI -n 上证指数     # CPI与上证指数关联分析
  python agent.py macro -i PPI -n 沪深300 -p 48  # PPI与沪深300(48个月)
  python agent.py demo                         # 运行完整演示
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 个股基本面分析命令
    fundamental_parser = subparsers.add_parser('fundamental', help='个股基本面分析')
    fundamental_parser.add_argument('symbol', type=str, help='股票代码 (如 600519)')
    fundamental_parser.add_argument('--save', '-s', action='store_true', help='保存报告')
    fundamental_parser.add_argument('--no-validation', action='store_true', help='跳过交叉验证')

    # 宏观经济分析命令
    macro_parser = subparsers.add_parser('macro', help='宏观经济关联性分析')
    macro_parser.add_argument('--indicator', '-i', type=str, default='CPI',
                              choices=['CPI', 'PPI', 'M2', 'GDP', '利率'],
                              help='宏观指标名称')
    macro_parser.add_argument('--index', '-n', type=str, default='上证指数',
                              help='股指名称')
    macro_parser.add_argument('--period', '-p', type=int, default=36,
                              help='分析周期(月)')
    macro_parser.add_argument('--save', '-s', action='store_true', help='保存报告')

    # 演示命令
    subparsers.add_parser('demo', help='运行演示')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    agent = InvestmentAgent()

    if args.command == 'fundamental':
        result = agent.analyze_stock(
            args.symbol,
            enable_validation=not args.no_validation
        )
        if args.save:
            agent.fundamental.save_report()

    elif args.command == 'macro':
        result = agent.analyze_macro(
            args.indicator,
            args.index,
            args.period
        )
        if args.save:
            agent.macro.save_report()

    elif args.command == 'demo':
        demo()


if __name__ == "__main__":
    main()

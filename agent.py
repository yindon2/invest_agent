"""
投资学AI Agent - 主程序入口
==========================
功能：整合所有分析技能，提供统一的调用接口
支持：个股基本面分析、宏观经济分析、可视化输出、交叉验证、风险人格选股

使用方法:
    python agent.py fundamental <股票代码>          # 个股基本面分析
    python agent.py macro --indicator CPI --index 上证指数  # 宏观经济分析
    python agent.py recommend F2-E2-C2-T2           # 根据IRTI风险人格推荐
    python agent.py claude                          # Claude Code启动方式
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


def show_claude_startup():
    """显示Claude Code启动方式"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                🐧 企鹅奇才 · Claude Code 启动方式            ║
╚══════════════════════════════════════════════════════════════╝

方式一：在 Claude Code 中直接运行分析命令
—————————————————————————————————————————————
  claude "分析贵州茅台 600519 的基本面"
  claude "CPI与上证指数的关联性如何？"
  claude "帮我写一份完整的投资分析报告"

方式二：作为 Claude Code Agent 技能加载
—————————————————————————————————————————————
  在 CLAUDE.md 中添加本 Agent 路径，然后：
  claude "运行 invest-agent fundamental 600519"

方式三：本地 Python 直接运行
—————————————————————————————————————————————
  python agent.py demo                         # 运行完整演示
  python agent.py fundamental 600519           # 个股基本面分析
  python agent.py macro -i CPI -n 上证指数     # 宏观经济分析
  python agent.py recommend F2-E2-C2-T2        # 风险人格推荐

方式四：作为 pip 包安装后使用
—————————————————————————————————————————————
  pip install invest-agent                     # 安装
  invest-agent fundamental 600519              # 命令行使用

📖 详细文档：https://github.com/yindon2/invest_agent
""")


# ========== IRTI 风险人格类型 → 股票推荐 ==========
# 免责声明：以下推荐仅供参考与教学研究，不构成任何投资建议。
# 股市有风险，投资需谨慎。所有投资决策风险由投资者自行承担。

IRTI_STOCK_MAP = {
    '保守型': {
        'label': '保守型投资者',
        'desc': '风险承受能力较低，适合稳定收益型标的',
        'stocks': [
            {'code': '601398', 'name': '工商银行', 'reason': '国有大行，分红稳定，股价波动小，适合保守型长期持有'},
            {'code': '600900', 'name': '长江电力', 'reason': '水电龙头，现金流充沛，防御性强，股息率稳定'},
            {'code': '600519', 'name': '贵州茅台', 'reason': '高端消费龙头，品牌护城河极深，长期稳健增长'},
        ]
    },
    '稳健型': {
        'label': '稳健型投资者',
        'desc': '风险承受能力中等，适合均衡配置',
        'stocks': [
            {'code': '600036', 'name': '招商银行', 'reason': '零售银行标杆，风控优秀，兼具成长与分红'},
            {'code': '000333', 'name': '美的集团', 'reason': '家电龙头，全球化布局，业务多元化抗风险能力强'},
            {'code': '600887', 'name': '伊利股份', 'reason': '乳业龙头，消费刚需，业绩稳健增长'},
        ]
    },
    '进取型': {
        'label': '进取型投资者',
        'desc': '风险承受能力较高，适合成长性标的',
        'stocks': [
            {'code': '300750', 'name': '宁德时代', 'reason': '动力电池全球龙头，新能源赛道高成长'},
            {'code': '300760', 'name': '迈瑞医疗', 'reason': '医疗器械龙头，国产替代空间大，业绩持续高增'},
            {'code': '688981', 'name': '中芯国际', 'reason': '晶圆代工龙头，半导体国产化核心标的'},
        ]
    }
}


def get_risk_level(risk_code: str) -> str:
    """
    解析IRTI风险人格代码，返回风险等级

    参数:
        risk_code: IRTI风险代码，格式如 "F2-E2-C2-T2"

    返回:
        '保守型' | '稳健型' | '进取型'
    """
    try:
        risk_code = risk_code.strip().upper()
        parts = risk_code.split('-')
        if len(parts) != 4:
            raise ValueError("格式错误")

        scores = []
        for p in parts:
            if p[0] not in ('F', 'E', 'C', 'T'):
                raise ValueError("维度错误")
            scores.append(int(p[1]))

        avg = sum(scores) / 4
        if avg <= 2.0:
            return '保守型'
        elif avg <= 3.0:
            return '稳健型'
        else:
            return '进取型'
    except Exception:
        return None


def recommend_by_risk(risk_code: str):
    """
    根据IRTI风险人格类型推荐3只股票（仅供参考研究）

    参数:
        risk_code: IRTI风险代码，如 "F2-E2-C2-T2"

    输出股票推荐（含免责声明）
    """
    from skills.fundamental import FundamentalAnalysisSkill
    from datetime import datetime

    print("\n" + "=" * 70)
    print("     🐧 企鹅奇才 · IRTI风险人格选股参考")
    print("     ⚠️  以下内容仅供教学研究参考，不构成投资建议")
    print("=" * 70)

    level = get_risk_level(risk_code)

    if level is None:
        print(f"\n❌ 风险代码格式错误: {risk_code}")
        print("   正确格式示例: F2-E2-C2-T2")
        print("   格式说明: F{1-4}-E{1-4}-C{1-4}-T{1-4}")
        print("   例如: F3-E2-C3-T2 表示 财务强韧-情绪中庸-专业认知-战术资金")
        return

    profile = IRTI_STOCK_MAP[level]
    dim_names = {
        'F': ('财务承载力', ['脆弱', '稳健', '强韧', '极高']),
        'E': ('情绪波动性', ['敏感', '中庸', '冷静', '冷漠']),
        'C': ('认知复杂度', ['基础', '进阶', '专业', '构建']),
        'T': ('流动性周期', ['超短钱', '战术钱', '战略钱', '永续钱'])
    }

    print(f"\n📋 输入的风险代码: {risk_code}")
    print(f"📊 风险等级评估: {level} — {profile['label']}")
    print(f"📝 特征描述: {profile['desc']}")

    try:
        parts = risk_code.split('-')
        print(f"\n📐 四维分析:")
        for i, p in enumerate(parts):
            dim = p[0]
            lv = int(p[1])
            name, levels = dim_names[dim]
            print(f"   {dim} ({name}): 第{lv}级 — {levels[lv-1]}")
    except Exception:
        pass

    # ====== 核心推荐（带强免责声明）======
    print(f"""

{'╔' + '═'*68 + '╗'}
{'║' + ' '*68 + '║'}
{'║  ⚠️  重 要 免 责 声 明 ⚠️' + ' '*44 + '║'}
{'║' + ' '*68 + '║'}
{'║  以下推荐的3只股票仅基于IRTI风险人格类型的学术研究匹配。' + ' '*4 + '║'}
{'║  ★ 不构成任何形式的购买建议或购买推荐 ★' + ' '*25 + '║'}
{'║  ★ 不构成任何投资建议，仅供参考 ★' + ' '*32 + '║'}
{'║  ★ 股市有风险，投资需谨慎 ★' + ' '*37 + '║'}
{'║  ★ 所有投资决策风险由投资者自行承担 ★' + ' '*27 + '║'}
{'║' + ' '*68 + '║'}
{'╚' + '═'*68 + '╝'}

{'─'*70}
   📌 针对 {profile['label']} ({risk_code}) 的参考匹配标的
{'─'*70}""")

    for i, stock in enumerate(profile['stocks'], 1):
        print(f"""
  [{i}] {stock['name']} ({stock['code']})
      ├ 匹配逻辑: {stock['reason']}
      └ 详细分析: python agent.py fundamental {stock['code']}""")

    print(f"""

{'─'*70}
  ⚠️ 再 次 提 醒

  以上内容由AI Agent基于风险人格类型自动匹配生成，
  仅供参考与学术研究使用。

  📌 不构成任何投资建议或购买推荐
  📌 过往表现不代表未来收益
  📌 投资有风险，入市需谨慎
  📌 请根据自身情况独立决策

  建议使用本Agent的 fundamental 命令进行详细的个股
  基本面分析（杜邦分析、财务健康评分等）后再做决策。

  运行示例:
    python agent.py fundamental {profile['stocks'][0]['code']}
{'─'*70}

  分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")


# ========== Claude Code 集成启动方式 ==========


def recommend_main():
    """风险人格推荐命令行入口"""
    parser = argparse.ArgumentParser(description='IRTI风险人格选股推荐')
    parser.add_argument('risk_code', type=str, nargs='?',
                       help='IRTI风险代码，格式如 F2-E2-C2-T2')
    parser.add_argument('--list', '-l', action='store_true',
                       help='列出所有风险等级对应的推荐标的')

    args = parser.parse_args(sys.argv[2:])

    if args.list:
        print(f"\n{'='*60}")
        print("     IRTI风险人格等级 · 所有推荐标的概览")
        print(f"{'='*60}")
        for level_key in ['保守型', '稳健型', '进取型']:
            profile = IRTI_STOCK_MAP[level_key]
            print(f"\n── {profile['label']} ── {profile['desc']}")
            for s in profile['stocks']:
                print(f"   {s['code']} {s['name']} — {s['reason']}")
        print()
        return

    if not args.risk_code:
        print("请提供IRTI风险代码，例如: python agent.py recommend F2-E2-C2-T2")
        print("或者使用 --list 查看所有推荐标的")
        return

    recommend_by_risk(args.risk_code)


def claude_main():
    """Claude启动方式命令行入口"""
    show_claude_startup()
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
  python agent.py recommend F2-E2-C2-T2        # 根据IRTI风险人格推荐股票
  python agent.py recommend --list             # 查看所有推荐标的
  python agent.py claude                       # Claude Code启动方式
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

    # 风险人格选股命令
    recommend_parser = subparsers.add_parser('recommend', help='根据IRTI风险人格推荐股票（仅供参考）')
    recommend_parser.add_argument('risk_code', type=str, nargs='?',
                                  help='IRTI风险代码，格式如 F2-E2-C2-T2')
    recommend_parser.add_argument('--list', '-l', action='store_true',
                                  help='列出所有推荐标的')

    # Claude启动方式
    subparsers.add_parser('claude', help='显示Claude Code启动方式')

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

    elif args.command == 'recommend':
        if args.list:
            recommend_main()
        elif args.risk_code:
            recommend_by_risk(args.risk_code)
        else:
            print("请提供IRTI风险代码，例如: python agent.py recommend F2-E2-C2-T2")
            print("或使用: python agent.py recommend --list 查看所有推荐标的")

    elif args.command == 'claude':
        show_claude_startup()

    elif args.command == 'demo':
        demo()


if __name__ == "__main__":
    main()

"""
企鹅奇才 · 交互式 Web UI
========================
基于 Flask 的聊天式投资分析界面，支持多轮对话上下文 + API 密钥配置。
"""
import sys, os, json, re
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agent import InvestmentAgent, recommend_by_risk, get_risk_level, IRTI_STOCK_MAP
from api_config import api_config

# Fix Windows GBK encoding in stdout
if sys.stdout.encoding and sys.stdout.encoding.upper() == 'GBK':
    sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
agent = InvestmentAgent()

OUTPUT_DIR = Path(__file__).parent / 'outputs'

# ─── 对话上下文管理 ───
class Conversation:
    def __init__(self):
        self.history = []
        self.context = {
            'last_symbol': None,
            'last_analysis_type': None,
            'risk_profile': None,
            'mentioned_stocks': [],
        }

    def add(self, role, content, data=None):
        self.history.append({
            'role': role,
            'content': content,
            'time': datetime.now().strftime('%H:%M:%S'),
            'data': data or {}
        })

    def to_dict(self):
        return {
            'history': self.history[-20:],   # 保留最近20条
            'context': self.context
        }

conversations = {}

def get_conv(session_id):
    if session_id not in conversations:
        conversations[session_id] = Conversation()
    return conversations[session_id]

# ─── 增强分析函数 ───

INDUSTRY_BENCHMARKS = {
    '白酒': {'PE': 35, 'ROE': 20, '毛利率': 75, '净利率': 30, '营收增速': 15},
    '银行': {'PE': 6, 'ROE': 11, '毛利率': None, '净利率': 35, '营收增速': 3},
    '医药': {'PE': 40, 'ROE': 14, '毛利率': 60, '净利率': 12, '营收增速': 18},
    '新能源': {'PE': 45, 'ROE': 12, '毛利率': 25, '净利率': 8, '营收增速': 35},
    '科技': {'PE': 50, 'ROE': 15, '毛利率': 45, '净利率': 10, '营收增速': 25},
    '消费': {'PE': 30, 'ROE': 18, '毛利率': 40, '净利率': 12, '营收增速': 12},
    '房地产': {'PE': 10, 'ROE': 8, '毛利率': 30, '净利率': 10, '营收增速': -5},
    '证券': {'PE': 22, 'ROE': 9, '毛利率': None, '净利率': 30, '营收增速': 10},
}

def guess_industry(symbol):
    if symbol.startswith('6'):
        code_num = int(symbol)
        if 600000 <= code_num < 600100: return '银行'
        if 600500 <= code_num < 600600: return '能源'
        if 600800 <= code_num < 600900: return '消费'
        if 601000 <= code_num < 601500: return '证券'
        if 601300 <= code_num < 601400: return '银行'
    elif symbol.startswith('0'):
        code_num = int(symbol)
        if 0 <= code_num < 1000: return '消费'
        if 300000 <= code_num < 301000: return '科技'
    elif symbol.startswith('3'):
        return '科技'
    if symbol == '600519': return '白酒'
    if symbol == '000333': return '消费'
    if symbol == '300750': return '新能源'
    if symbol == '600036': return '银行'
    if symbol == '601398': return '银行'
    return '消费'

def industry_comparison(symbol, financial_data):
    industry = guess_industry(symbol)
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, {})
    if not benchmarks:
        return None

    metrics = financial_data.get('核心指标', {})
    pe = metrics.get('市盈率PE')
    roe = metrics.get('净资产收益率ROE')
    gross = metrics.get('毛利率')
    net_m = metrics.get('净利率')

    comparisons = []
    if pe and benchmarks.get('PE'):
        pe_bench = benchmarks['PE']
        diff = (pe - pe_bench) / pe_bench * 100
        comparisons.append({
            'name': '市盈率PE',
            'value': pe,
            'benchmark': pe_bench,
            'diff': round(diff, 1),
            'verdict': '高于行业' if diff > 10 else ('低于行业' if diff < -10 else '接近行业')
        })
    if roe and benchmarks.get('ROE'):
        diff = roe - benchmarks['ROE']
        comparisons.append({
            'name': 'ROE(%)',
            'value': roe,
            'benchmark': benchmarks['ROE'],
            'diff': round(diff, 1),
            'verdict': '高于行业' if diff > 3 else ('低于行业' if diff < -3 else '接近行业')
        })
    if gross and benchmarks.get('毛利率'):
        diff = gross - benchmarks['毛利率']
        comparisons.append({
            'name': '毛利率(%)',
            'value': gross,
            'benchmark': benchmarks['毛利率'],
            'diff': round(diff, 1),
            'verdict': '高于行业' if diff > 5 else ('低于行业' if diff < -5 else '接近行业')
        })
    return {'industry': industry, 'comparisons': comparisons, 'benchmarks': benchmarks}

def technical_signals(result):
    dupont = result.get('杜邦分析', {})
    health = result.get('健康评分', {})
    signals = []

    roe = dupont.get('ROE')
    if roe is None:
        signals.append(('⚪', '数据不足', '无法获取ROE数据'))
        return signals

    if roe >= 20: signals.append(('🟢', '盈利能力强劲', f'ROE {roe:.1f}% 超过20%，优秀'))
    elif roe >= 15: signals.append(('🔵', '盈利能力良好', f'ROE {roe:.1f}% 在15-20%之间'))
    elif roe >= 10: signals.append(('🟡', '盈利能力一般', f'ROE {roe:.1f}% 在10-15%之间'))
    else: signals.append(('🔴', '盈利能力需关注', f'ROE {roe:.1f}% 低于10%'))

    net_profit = dupont.get('净利率', 0)
    if net_profit >= 20: signals.append(('🟢', '高利润率', f'净利率 {net_profit:.1f}%'))
    elif net_profit >= 10: signals.append(('🔵', '利润率良好', f'净利率 {net_profit:.1f}%'))
    else: signals.append(('🟡', '利润率偏低', f'净利率 {net_profit:.1f}%'))

    z = health.get('Z值', 0)
    if isinstance(z, (int, float)):
        if z > 2.99: signals.append(('🟢', '财务安全', f'Z值 {z:.2f} > 2.99，破产风险低'))
        elif z > 1.81: signals.append(('🟡', '财务关注', f'Z值 {z:.2f} 在1.81-2.99之间'))
        else: signals.append(('🔴', '财务危险', f'Z值 {z:.2f} < 1.81，破产风险高'))

    turnover = dupont.get('资产周转率', 0)
    if turnover >= 1: signals.append(('🟢', '运营效率高', f'周转率 {turnover:.2f}'))
    elif turnover >= 0.5: signals.append(('🔵', '运营效率一般', f'周转率 {turnover:.2f}'))
    else: signals.append(('🟡', '运营效率偏低', f'周转率 {turnover:.2f}'))

    return signals

def financial_rating(result):
    dupont = result.get('杜邦分析', {})
    health = result.get('健康评分', {})
    score = 0
    max_score = 100

    roe = dupont.get('ROE')
    if roe is None:
        return 'N/A', '数据不足', '#888888'

    if roe >= 20: score += 25
    elif roe >= 15: score += 20
    elif roe >= 10: score += 15
    else: score += 5

    net_m = dupont.get('净利率', 0)
    if net_m >= 20: score += 25
    elif net_m >= 10: score += 20
    elif net_m >= 5: score += 15
    else: score += 5

    z = health.get('Z值', 0)
    if isinstance(z, (int, float)):
        if z > 2.99: score += 25
        elif z > 1.81: score += 15
        else: score += 5

    turnover = dupont.get('资产周转率', 0)
    if turnover >= 1: score += 25
    elif turnover >= 0.5: score += 15
    elif turnover >= 0.3: score += 10
    else: score += 5

    if score >= 80: return 'A', '优秀', '#27ae60'
    if score >= 60: return 'B', '良好', '#2980b9'
    if score >= 40: return 'C', '一般', '#f39c12'
    return 'D', '关注', '#e74c3c'

def peer_stocks(symbol):
    industry = guess_industry(symbol)
    peers_map = {
        '白酒': [('600519', '贵州茅台'), ('000858', '五粮液'), ('002304', '洋河股份')],
        '银行': [('601398', '工商银行'), ('600036', '招商银行'), ('601166', '兴业银行')],
        '消费': [('000333', '美的集团'), ('600887', '伊利股份'), ('600690', '海尔智家')],
        '科技': [('300750', '宁德时代'), ('002415', '海康威视'), ('000725', '京东方A')],
        '新能源': [('300750', '宁德时代'), ('601012', '隆基绿能'), ('002129', '中环股份')],
        '证券': [('600030', '中信证券'), ('601211', '国泰君安'), ('600837', '海通证券')],
    }
    return peers_map.get(industry, [])

def format_report_markdown(result):
    info = result.get('基本信息', {})
    symbol = result.get('股票代码', '')
    dupont = result.get('杜邦分析', {})
    health = result.get('健康评分', {})
    validation = result.get('交叉验证', {})

    rating_grade, rating_label, rating_color = financial_rating(result)
    signals = technical_signals(result)
    industry_data = industry_comparison(symbol, result.get('财务数据', {}))
    peers = peer_stocks(symbol)

    def safe(val, fmt_char=''):
        if val is None:
            return 'N/A'
        try:
            v = float(val)
            if fmt_char:
                return f"{v:.2f}{fmt_char}"
            return f"{v:.2f}"
        except:
            return str(val)

    data_src = info.get('_data_source', dupont.get('数据来源', ''))
    src_note = ''
    if data_src and '估算' in str(data_src):
        src_note = f'\n> [i] 数据来源: {data_src}（配置Tushare Token可获取精确数据）\n'

    md = f"""## 📊 {info.get('名称', symbol)} ({symbol}) 基本面分析

<div class="rating-badge" style="background:{rating_color}">{rating_grade} · {rating_label}</div>

### 📋 核心数据
| 指标 | 数值 |
|------|------|
| 最新价 | {safe(info.get('最新价'))} |
| 涨跌幅 | {safe(info.get('涨跌幅'), '%')} |
| 市盈率 | {safe(info.get('市盈率'))} |
| 市净率 | {safe(info.get('市净率'))} |
{src_note}"""

    if signals:
        md += "\n### 📈 技术信号\n"
        for icon, label, desc in signals:
            md += f"- {icon} **{label}**: {desc}\n"

    if dupont and dupont.get('ROE') is not None:
        roe = dupont['ROE']
        net_m = dupont.get('净利率', 0)
        turnover = dupont.get('资产周转率', 0)
        equity_m = dupont.get('权益乘数', 0)
        dsrc = dupont.get('数据来源', '')
        dsrc_note = f'\n> [i] {dsrc}' if dsrc and '估算' in str(dsrc) else ''
        md += f"""
### 🔬 杜邦分析
| 指标 | 数值 | 解读 |
|------|------|------|
| **ROE** | {roe:.2f}% | 核心盈利能力 |
| 净利率 | {net_m:.2f}% | 产品盈利能力 |
| 周转率 | {turnover:.2f} | 运营效率 |
| 权益乘数 | {equity_m:.2f} | 财务杠杆 |
{dsrc_note}"""

    if isinstance(health.get('Z值'), (int, float)):
        z = health['Z值']
        z_color = '#27ae60' if z > 2.99 else ('#f39c12' if z > 1.81 else '#e74c3c')
        md += f"""
### 🏥 财务健康 (Altman Z-Score)
<div class="z-score" style="color:{z_color}">Z = {z:.2f} — {health.get('风险等级', '')}</div>
"""

    if industry_data:
        md += f"\n### 🏭 行业对比 ({industry_data['industry']})\n"
        for c in industry_data['comparisons']:
            icon = '📈' if '高于' in c['verdict'] else ('📉' if '低于' in c['verdict'] else '📊')
            md += f"- {icon} {c['name']}: **{c['value']}** vs 行业 {c['benchmark']} ({c['verdict']})\n"

    if peers:
        md += "\n### 🏢 同业对比\n"
        for code, name in peers:
            md += f"- [{name}](stock:{code})\n"

    if validation:
        cred = validation.get('整体可信度', 0)
        md += f"\n### ✅ 数据可信度\n> 整体可信度: **{cred:.1f}%**\n"

    md += f"\n*分析时间: {result.get('分析时间', '')}*"
    return md

def format_macro_markdown(result):
    indicator = result.get('宏观指标', '')
    index_name = result.get('股指', '')
    corr = result.get('相关性分析', {})
    causality = result.get('因果检验', {})
    report = result.get('分析报告', '')

    pearson = corr.get('Pearson', {})
    r = pearson.get('相关系数', 0)

    md = f"""## 📉 宏观经济分析

**{indicator} vs {index_name}**

### 🔗 相关性
- Pearson相关系数: **{r}**
- 相关性强度: {pearson.get('相关性强度', 'N/A')}
- 统计显著性: {pearson.get('显著性', 'N/A')}

### 📊 滚动相关性
- 均值: {corr.get('滚动相关系数_均值', 'N/A')}
- 标准差: {corr.get('滚动相关系数_标准差', 'N/A')}
"""

    gc = causality.get('格兰杰因果检验', {})
    if gc:
        x2y = gc.get('x导致y', {})
        for lag, res in x2y.items() if isinstance(x2y, dict) else []:
            if isinstance(res, dict) and '结论' in res:
                md += f"- {lag}: {res['结论']}\n"

    md += f"\n*分析时间: {result.get('分析时间', '')}*"
    return md

def format_recommend_markdown(risk_code):
    level = get_risk_level(risk_code)
    if not level:
        return "❌ 风险代码格式错误。正确格式: F2-E2-C2-T2"

    profile = IRTI_STOCK_MAP[level]
    md = f"""## 🎯 IRTI 选股推荐

**风险人格**: {profile['label']}
**特征**: {profile['desc']}

### 推荐标的
"""
    for i, stock in enumerate(profile['stocks'], 1):
        md += f"""
**{i}. {stock['name']} ({stock['code']})**
- 📝 {stock['reason']}
- 💡 `agent.py fundamental {stock['code']}`
"""

    md += "\n> ⚠️ **免责声明**: 以上推荐仅基于IRTI风险人格类型的学术研究匹配，不构成投资建议。"
    return md

# ─── API 路由 ───

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/charts/<path:filename>')
def serve_chart(filename):
    return send_from_directory(OUTPUT_DIR / 'charts', filename)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    msg = data.get('message', '').strip()
    session_id = data.get('session_id', 'default')
    risk_code = data.get('risk_code', '')

    conv = get_conv(session_id)
    if risk_code:
        conv.context['risk_profile'] = risk_code

    if not msg:
        return jsonify({'reply': '请输入股票代码、分析指令或问题。', 'conv': conv.to_dict()})

    # 分析用户意图
    msg_lower = msg.lower()

    # 识别股票代码 (6位数字)
    code_match = re.search(r'\b(\d{6})\b', msg)

    # 识别IRTI风险代码 (如 F2-E2-C2-T2)
    risk_match = re.search(r'([FfEeCcTt]\d[-][FfEeCcTt]\d[-][FfEeCcTt]\d[-][FfEeCcTt]\d)', msg)

    # 识别宏观分析
    macro_keywords = ['cpi', 'ppi', 'm2', 'gdp', '利率', '宏观', '经济', '通胀', '指数', '上证']
    is_macro = any(kw in msg_lower or kw in msg for kw in macro_keywords)

    # 识别推荐
    recommend_keywords = ['推荐', '选股', '建议', '风险人格', 'irti', 'reco']
    is_recommend = any(kw in msg_lower or kw in msg for kw in recommend_keywords)

    try:
        # 注入已配置的 API keys
        tushare_token = api_config.get('tushare', 'token')
        if tushare_token:
            os.environ['TUSHARE_TOKEN'] = tushare_token

        # 1. IRTI风险代码推荐
        if risk_match:
            code = risk_match.group(1).upper()
            conv.add('user', msg)
            md = format_recommend_markdown(code)
            conv.add('assistant', md, {'type': 'recommend', 'risk_code': code})
            conv.context['risk_profile'] = code
            return jsonify({'reply': md, 'conv': conv.to_dict()})

        # 2. 宏观经济分析
        if is_macro and not code_match:
            conv.add('user', msg)
            indicator = 'CPI'
            for kw in ['PPI', 'CPI', 'M2', 'GDP', '利率']:
                if kw in msg.upper() or kw in msg:
                    indicator = kw
                    break
            index_name = '上证指数'
            for idx in ['沪深300', '上证50', '创业板指', '深证成指', '上证指数']:
                if idx in msg:
                    index_name = idx
                    break

            result = agent.analyze_macro(indicator, index_name, 36)
            md = format_macro_markdown(result)

            charts = result.get('图表', {})
            for name, path in charts.items():
                fname = os.path.basename(path)
                md += f'\n![{name}](/api/charts/{fname})\n'

            conv.add('assistant', md, {'type': 'macro', 'indicator': indicator, 'index': index_name})
            return jsonify({'reply': md, 'conv': conv.to_dict()})

        # 3. 推荐
        if is_recommend and not code_match:
            conv.add('user', msg)
            risk = conv.context.get('risk_profile', 'F2-E2-C2-T2')
            md = format_recommend_markdown(risk)
            conv.add('assistant', md, {'type': 'recommend'})
            return jsonify({'reply': md, 'conv': conv.to_dict()})

        # 4. 个股基本面分析
        if code_match:
            symbol = code_match.group(1)
            conv.add('user', msg)
            conv.context['last_symbol'] = symbol
            if symbol not in conv.context['mentioned_stocks']:
                conv.context['mentioned_stocks'].append(symbol)

            result = agent.analyze_stock(symbol)
            md = format_report_markdown(result)

            charts = result.get('图表', {})
            for name, path in charts.items():
                if os.path.exists(path):
                    fname = os.path.basename(path)
                    md += f'\n![{name}](/api/charts/{fname})\n'

            # 附加上下文建议
            md += '\n\n---\n💡 **继续分析**: '
            peers = peer_stocks(symbol)
            if peers:
                for code, name in peers[:2]:
                    if code != symbol:
                        md += f'`{code}` '
            md += ' `macro CPI` `recommend`'

            conv.add('assistant', md, {'type': 'fundamental', 'symbol': symbol})
            return jsonify({'reply': md, 'conv': conv.to_dict()})

        # 5. 问候/通用对话
        greetings = ['你好', 'hi', 'hello', '嗨', '早上好', '下午好', '晚上好']
        if any(g in msg_lower or g in msg for g in greetings):
            risk = conv.context.get('risk_profile', '')
            reply = f"""## 👋 你好！我是企鹅奇才

我可以帮你做以下分析：

**📊 个股基本面分析**
输入股票代码，如 `600519`、`000001`

**📉 宏观经济分析**
输入如 `CPI与上证指数的关系`、`PPI分析`

**🎯 IRTI风险选股**
输入如 `F2-E2-C2-T2` 或 `帮我推荐股票`

**📌 示例:**
- `分析600519` — 贵州茅台基本面
- `CPI对股市的影响` — 宏观分析
- `推荐股票` — 基于你的风险人格
"""
            if risk:
                reply += f'\n当前风险人格: `{risk}`'
            conv.add('assistant', reply, {'type': 'greeting'})
            return jsonify({'reply': reply, 'conv': conv.to_dict()})

        # 6. 帮助
        reply = """## 🤖 企鹅奇才 AI Agent

支持的命令:

| 类型 | 示例 |
|------|------|
| 个股分析 | `600519` `分析贵州茅台` |
| 宏观分析 | `CPI与上证指数` `PPI对股市影响` |
| IRTI选股 | `F2-E2-C2-T2` `推荐股票` |
| 行业对比 | 分析后自动生成 |
| 帮助 | `help` `你好` |

**分析流程**: 输入股票代码 → 查看基本面 → 行业对比 → 技术信号 → 同业比较
"""
        conv.add('assistant', reply, {'type': 'help'})
        return jsonify({'reply': reply, 'conv': conv.to_dict()})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'reply': f'❌ 分析出错: {str(e)}', 'conv': conv.to_dict()})

@app.route('/api/reset', methods=['POST'])
def reset():
    data = request.get_json()
    session_id = data.get('session_id', 'default')
    conversations[session_id] = Conversation()
    return jsonify({'status': 'ok'})

@app.route('/api/risk_profiles', methods=['GET'])
def risk_profiles():
    return jsonify({
        'profiles': [
            {'code': 'F1-E1-C1-T1', 'label': '极度保守', 'desc': '财务脆弱+情绪敏感+认知基础+超短资金'},
            {'code': 'F2-E2-C2-T2', 'label': '保守型', 'desc': '财务稳健+情绪中庸+认知进阶+战术资金'},
            {'code': 'F3-E2-C3-T3', 'label': '稳健型', 'desc': '财务强韧+情绪冷静+专业认知+战略资金'},
            {'code': 'F4-E3-C4-T4', 'label': '进取型', 'desc': '财务极高+情绪冷静+知识构建+永续资金'},
        ]
    })

# ─── API 配置路由 ───

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取所有 API 配置状态（隐藏完整 token）"""
    return jsonify({'apis': api_config.status()})

@app.route('/api/config', methods=['POST'])
def save_config():
    """保存 API 配置"""
    data = request.get_json()
    name = data.get('name', '')
    token = data.get('token', '')
    enabled = data.get('enabled', True)
    if not name:
        return jsonify({'ok': False, 'msg': 'API 名称不能为空'})
    if not token:
        return jsonify({'ok': False, 'msg': 'API Key/Token 不能为空'})
    api_config.set(name, token, enabled)
    return jsonify({'ok': True, 'msg': f'{name} 配置已保存', 'status': api_config.status()})

@app.route('/api/config/<name>', methods=['DELETE'])
def delete_config(name):
    """删除 API 配置"""
    api_config.delete(name)
    return jsonify({'ok': True, 'msg': f'{name} 配置已删除', 'status': api_config.status()})

@app.route('/api/config/test/<name>', methods=['POST'])
def test_config(name):
    """测试 API 连接"""
    if name == 'tushare':
        result = api_config.test_tushare()
    elif name == 'openai':
        result = api_config.test_openai()
    elif name == 'deepseek':
        result = api_config.test_deepseek()
    else:
        result = {'ok': False, 'msg': f'不支持的 API: {name}'}
    return jsonify(result)

@app.route('/api/config/available', methods=['GET'])
def available_apis():
    """列出所有可配置的 API"""
    return jsonify({
        'apis': [
            {
                'id': 'tushare',
                'name': 'Tushare Pro',
                'site': 'https://tushare.pro',
                'description': '提供A股行情、财务指标、财务报表等完整数据',
                'howto': '1. 注册 tushare.pro → 2. 个人主页获取 Token → 3. 粘贴到下方',
                'icon': '📊',
                'doc_url': 'https://tushare.pro/document/1'
            },
            {
                'id': 'openai',
                'name': 'OpenAI / Claude API',
                'site': 'https://platform.openai.com',
                'description': '用于智能分析报告生成、自然语言交互增强',
                'howto': '1. 创建 API Key → 2. 复制 sk- 开头的密钥 → 3. 粘贴到下方',
                'icon': '🤖',
                'doc_url': 'https://platform.openai.com/api-keys'
            },
            {
                'id': 'deepseek',
                'name': 'DeepSeek API',
                'site': 'https://platform.deepseek.com',
                'description': 'DeepSeek 大模型 API，用于智能分析报告生成、自然语言交互增强',
                'howto': '1. 注册 platform.deepseek.com → 2. 创建 API Key → 3. 粘贴到下方',
                'icon': '🧠',
                'doc_url': 'https://platform.deepseek.com/api_keys'
            },
            {
                'id': 'akshare',
                'name': 'AKShare (免费)',
                'site': 'https://akshare.akfamily.xyz',
                'description': '开源免费金融数据接口，无需配置即可使用',
                'howto': '无需配置，已内置可用。如需 token 可忽略此项。',
                'icon': '🔓',
                'doc_url': 'https://akshare.akfamily.xyz/'
            }
        ]
    })

if __name__ == '__main__':
    print("=" * 50)
    print("Penguin Genius - Web UI 启动")
    print("http://localhost:5000")
    print("=" * 50)
    app.run(host='127.0.0.1', port=5000, debug=False)

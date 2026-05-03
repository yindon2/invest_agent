# 投资学AI Agent 运行说明

> 基于Claude Code Agent能力框架，实现投资学核心功能的智能化分析

---

## 一、运行环境

| 项目 | 要求 |
|------|------|
| Python | 3.10+ (测试版本: 3.14.3) |
| 操作系统 | Windows / macOS / Linux |

## 二、核心依赖库

```
akshare>=1.18.0        # 中国金融数据接口
pandas>=2.0.0          # 数据处理
numpy>=1.24.0          # 数值计算
matplotlib>=3.7.0      # 可视化
scipy>=1.10.0          # 统计分析
statsmodels>=0.14.0    # 时间序列分析（可选）
```

安装命令：
```bash
pip install akshare pandas numpy matplotlib scipy statsmodels
```

## 三、项目结构

```
investment_agent/
├── agent.py              # 主程序入口
├── skills/               # 技能模块
│   ├── fundamental.py    # 个股基本面分析
│   ├── macro_analysis.py # 宏观经济分析
│   ├── visualization.py  # 可视化输出
│   └── cross_validate.py # 交叉验证(创新)
├── tools/                # 工具模块
│   ├── data_fetcher.py   # 数据获取
│   ├── financial_metrics.py # 财务指标计算
│   └── stat_analysis.py  # 统计分析
└── outputs/              # 输出目录
    ├── reports/          # 分析报告
    └── charts/           # 图表文件
```

## 四、关键指令示例

### 4.1 个股基本面分析

```bash
# 分析贵州茅台(600519)
python agent.py fundamental 600519

# 分析并保存报告
python agent.py fundamental 600519 --save

# 跳过交叉验证
python agent.py fundamental 000001 --no-validation
```

**输出示例**：
- 杜邦分析结果（ROE分解）
- Altman Z-Score财务健康评分
- 数据交叉验证可信度
- 可视化图表（PNG格式）

### 4.2 宏观经济关联性分析

```bash
# CPI与上证指数关联分析
python agent.py macro -i CPI -n 上证指数

# PPI与沪深300分析（48个月周期）
python agent.py macro -i PPI -n 沪深300 -p 48

# 利率与创业板指分析
python agent.py macro -i 利率 -n 创业板指
```

**支持的宏观指标**：`CPI`、`PPI`、`M2`、`GDP`、`利率`

**支持的股指**：`上证指数`、`深证成指`、`创业板指`、`沪深300`、`上证50`

**输出示例**：
- Pearson/Spearman相关系数
- 格兰杰因果检验结果
- 领先滞后关系分析
- 滚动相关系数图

### 4.3 运行演示

```bash
# 运行完整功能演示
python agent.py demo
```

## 五、核心功能说明

### 功能1：个股基本面数据抓取与财务指标解读

| 分析项 | 说明 |
|--------|------|
| 财务指标 | PE、PB、ROE、毛利率、净利率、负债率 |
| 杜邦分析 | ROE = 净利率 × 资产周转率 × 权益乘数 |
| 财务健康 | Altman Z-Score破产预警模型 |
| 数据源 | akshare（东方财富、同花顺） |

### 功能2：宏观经济指标与股市关联性分析

| 分析项 | 说明 |
|--------|------|
| 相关性分析 | Pearson、Spearman、滚动相关系数 |
| 因果检验 | 格兰杰因果检验（双向） |
| 领先滞后 | 交叉相关分析识别领先关系 |
| 平稳性检验 | ADF检验、KPSS检验 |

### 功能3：可视化输出

- 财务指标雷达图
- 杜邦分析分解图
- 财务健康仪表盘
- 时间序列趋势图
- 相关性热力图
- 滚动相关系数图

### 功能4：交叉验证（创新功能）

| 验证维度 | 说明 |
|----------|------|
| 合理性检验 | 数值是否在正常范围内 |
| 一致性检验 | 与历史数据是否矛盾 |
| 行业对比 | 与行业均值差异是否合理 |
| 可信度评分 | 综合评估数据可靠性 |

## 六、输出文件

运行后生成：

```
outputs/
├── reports/
│   ├── 600519_fundamental_report.md    # 基本面分析报告
│   └── CPI_上证指数_macro_report.md    # 宏观分析报告
└── charts/
    ├── dupont_xxx.png                   # 杜邦分析图
    ├── health_gauge_xxx.png             # 健康仪表盘
    ├── radar_xxx.png                    # 雷达图
    └── macro_comparison_xxx.png         # 宏观对比图
```

## 七、常见问题

**Q: 数据获取失败？**
A: akshare依赖网络连接，请检查网络。部分数据可能有延迟。

**Q: 中文显示乱码？**
A: 确保系统安装了中文字体（SimHei或Microsoft YaHei）。

**Q: statsmodels模块缺失？**
A: 运行 `pip install statsmodels` 安装。

---

*投资学AI Agent - 基于Claude Code Agent能力框架*

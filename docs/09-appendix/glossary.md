# 术语表

## 缠论术语

| 中文 | 英文 | 代码中的表示 | 说明 |
|------|------|--------------|------|
| K线 | K-Line / Candlestick | KLine, KLineUnit | 价格数据的基本单位 |
| 合并K线 | Combined K-Line | KLine, klc | 处理了包含关系的K线 |
| 包含关系 | Inclusion | KLINE_DIR.INCLUDED | 两根K线高低点包含 |
| 分形 | Fractal | FX_TYPE | 顶底分形 |
| 顶分形 | Top Fractal | FX_TYPE.TOP | 中间K线最高 |
| 底分形 | Bottom Fractal | FX_TYPE.BOTTOM | 中间K线最低 |
| 笔 | Bi / Stroke | Bi | 连接顶底分形的线段 |
| 线段 | Segment | Seg | 由多笔构成的结构 |
| 中枢 | Zhongshu / Pivot | ZS | 多笔重叠区间 |
| 买卖点 | Buy Sell Point | BSPoint, bsp | 形态学买卖点 |
| 背驰 | Divergence | divergence_rate | 趋势力度减弱 |
| 区间套 | Nested Interval | QJT | 多级别联立分析 |
| 趋势 | Trend | - | 至少两个中枢 |
| 盘整 | Consolidation | - | 一个中枢 |

---

## 买卖点类型

| 类型 | 代码 | 说明 |
|------|------|------|
| 一类买卖点 | T1 / 1 | 趋势末端背驰点 |
| 盘整背驰 | T1P / 1p | 盘整走势中的背驰 |
| 二类买卖点 | T2 / 2 | 一类后第一次回调 |
| 类二买卖点 | T2S / 2s | 二类后类似结构 |
| 三类买卖点A | T3A / 3a | 中枢在一类后面 |
| 三类买卖点B | T3B / 3b | 中枢在一类前面 |

---

## 中枢术语

| 术语 | 说明 |
|------|------|
| ZG | 中枢高点（重叠区间上沿） |
| ZD | 中枢低点（重叠区间下沿） |
| GG | 中枢最高点（所有笔的最高） |
| DD | 中枢最低点（所有笔的最低） |
| 中枢延伸 | 新笔进入中枢区间 |
| 中枢合并 | 相邻中枢合并 |

---

## 代码缩写

| 缩写 | 全称 | 说明 |
|------|------|------|
| klu | KLine Unit | 单根K线 |
| klc | KLine Combine | 合并K线 |
| bi | Bi | 笔 |
| seg | Segment | 线段 |
| zs | Zhongshu | 中枢 |
| bsp | Buy Sell Point | 形态学买卖点 |
| cbsp | Custom BSP | 自定义买卖点 |
| fx | Fractal | 分形 |
| lv | Level | 级别 |
| conf | Config | 配置 |

---

## 技术指标

| 指标 | 英文 | 说明 |
|------|------|------|
| MACD | Moving Average Convergence Divergence | 指数平滑异同移动平均线 |
| DIF | Difference | MACD快线减慢线 |
| DEA | Signal Line | DIF的EMA |
| RSI | Relative Strength Index | 相对强弱指标 |
| KDJ | Stochastic Oscillator | 随机指标 |
| BOLL | Bollinger Bands | 布林线 |
| MA | Moving Average | 移动平均线 |
| Demark | Tom DeMark Indicator | 德马克指标 |

---

## 数据相关

| 术语 | 说明 |
|------|------|
| OHLC | Open/High/Low/Close 开高低收 |
| Volume | 成交量 |
| Turnover | 成交额 |
| Turnover Rate | 换手率 |
| QFQ | 前复权 |
| HFQ | 后复权 |

---

## K线级别

| 中文 | 英文 | 代码 |
|------|------|------|
| 1分钟 | 1 Minute | K_1M |
| 3分钟 | 3 Minutes | K_3M |
| 5分钟 | 5 Minutes | K_5M |
| 15分钟 | 15 Minutes | K_15M |
| 30分钟 | 30 Minutes | K_30M |
| 60分钟 | 60 Minutes | K_60M |
| 日线 | Daily | K_DAY |
| 周线 | Weekly | K_WEEK |
| 月线 | Monthly | K_MON |
| 季线 | Quarterly | K_QUARTER |
| 年线 | Yearly | K_YEAR |

---

## 完整版术语

| 术语 | 说明 |
|------|------|
| cbsp | Custom Buy Sell Point 自定义买卖点 |
| Strategy | 策略类 |
| Signal | 交易信号 |
| Feature | 特征 |
| Model | 机器学习模型 |
| AutoML | 自动机器学习 |
| Backtest | 回测 |
| TradeEngine | 交易引擎 |

---

## 配置术语

| 术语 | 说明 |
|------|------|
| bi_strict | 严格笔 |
| bi_fx_check | 分形检查方法 |
| seg_algo | 线段算法 |
| zs_combine | 中枢合并 |
| divergence_rate | 背驰比例 |
| trigger_step | 逐步回放 |

---

## 结束

恭喜你阅读完所有文档！如有问题，欢迎反馈。


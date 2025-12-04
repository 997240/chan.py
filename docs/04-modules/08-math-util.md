# 数学工具模块 (math_util)

## 模块概述

`math_util/` 模块提供各种技术指标的计算。

---

## 目录结构

```
math_util/
├── __init__.py
├── macd.py          # MACD指标
├── boll.py          # 布林线
├── demark.py        # Demark指标
├── kdj.py           # KDJ指标
├── rsi.py           # RSI指标
├── trend_line.py    # 趋势线
└── trend_model.py   # 趋势模型（均线等）
```

---

## MACD

### 配置

```python
config = ChanConfig({
    "macd": {
        "fast": 12,       # 快线周期
        "slow": 26,       # 慢线周期
        "signal": 9,      # 信号线周期
    }
})
```

### 访问

```python
klu = chan[0][-1][-1]  # 最后一根K线

print(f"DIF: {klu.macd.dif:.4f}")
print(f"DEA: {klu.macd.dea:.4f}")
print(f"MACD: {klu.macd.macd:.4f}")  # 红绿柱
```

### 属性

| 属性 | 说明 |
|------|------|
| dif | DIF值（快线-慢线） |
| dea | DEA值（DIF的EMA） |
| macd | MACD柱（DIF-DEA）*2 |

---

## 布林线 (BOLL)

### 配置

```python
config = ChanConfig({
    "boll_n": 20,  # 计算周期
})
```

### 访问

```python
klu = chan[0][-1][-1]

print(f"上轨: {klu.boll.UP:.2f}")
print(f"中轨: {klu.boll.MID:.2f}")
print(f"下轨: {klu.boll.DOWN:.2f}")
```

---

## 均线 (MA)

### 配置

```python
config = ChanConfig({
    "mean_metrics": [5, 10, 20, 60],  # 均线周期
})
```

### 访问

```python
klu = chan[0][-1][-1]

# 访问5日均线
ma5 = klu.trend[TREND_TYPE.MEAN][5]
print(f"MA5: {ma5:.2f}")
```

---

## 通道线

### 配置

```python
config = ChanConfig({
    "trend_metrics": [20],  # 周期
})
```

### 访问

```python
klu = chan[0][-1][-1]

# 20日最高价
high_20 = klu.trend[TREND_TYPE.MAX][20]

# 20日最低价
low_20 = klu.trend[TREND_TYPE.MIN][20]

print(f"20日高点: {high_20:.2f}")
print(f"20日低点: {low_20:.2f}")
```

---

## Demark 指标

### 配置

```python
config = ChanConfig({
    "cal_demark": True,
    "demark": {
        "demark_len": 9,        # setup完成长度
        "setup_bias": 4,        # setup比较偏移
        "countdown_bias": 2,    # countdown比较偏移
        "max_countdown": 13,    # 最大countdown数
    }
})
```

### 说明

Demark指标用于识别趋势耗尽：
- **Setup**: 连续N根K线收盘价高于/低于N根之前
- **Countdown**: Setup完成后的计数

---

## RSI 指标

### 配置

```python
config = ChanConfig({
    "cal_rsi": True,
    "rsi_cycle": 14,  # 计算周期
})
```

### 访问

```python
klu = chan[0][-1][-1]
print(f"RSI: {klu.rsi:.2f}")
```

### 解读

- RSI > 70: 超买
- RSI < 30: 超卖

---

## KDJ 指标

### 配置

```python
config = ChanConfig({
    "cal_kdj": True,
    "kdj_cycle": 9,  # 计算周期
})
```

### 访问

```python
klu = chan[0][-1][-1]
print(f"K: {klu.kdj.k:.2f}")
print(f"D: {klu.kdj.d:.2f}")
print(f"J: {klu.kdj.j:.2f}")
```

---

## 趋势线

趋势线用于绘制线段的支撑/阻力线。

### 绘图配置

```python
plot_para = {
    "seg": {
        "plot_trendline": True,
        "trendline_color": "r",
        "trendline_width": 3,
    }
}
```

---

## 在笔中使用指标

笔提供了多种基于指标的计算方法：

```python
from common.enums import MACD_ALGO

bi = chan[0].bi_list[-1]

# MACD峰值
peak = bi.cal_macd_metric(MACD_ALGO.PEAK, False)

# MACD面积
area = bi.cal_macd_metric(MACD_ALGO.AREA, False)

# 笔的斜率
slope = bi.cal_macd_metric(MACD_ALGO.SLOPE, False)

# 笔的涨跌幅
amp = bi.cal_macd_metric(MACD_ALGO.AMP, False)

# 成交量
volume = bi.cal_macd_metric(MACD_ALGO.VOLUME, False)

# RSI
rsi = bi.cal_macd_metric(MACD_ALGO.RSI, False)
```

---

## 使用示例

### 综合技术分析

```python
config = ChanConfig({
    "mean_metrics": [5, 20, 60],
    "trend_metrics": [20],
    "boll_n": 20,
    "cal_rsi": True,
    "cal_kdj": True,
})

chan = Chan(..., config=config)

# 获取最新K线
klu = chan[0][-1][-1]

# 价格与均线关系
ma5 = klu.trend[TREND_TYPE.MEAN][5]
ma20 = klu.trend[TREND_TYPE.MEAN][20]

if klu.close > ma5 > ma20:
    print("多头排列")
elif klu.close < ma5 < ma20:
    print("空头排列")

# RSI判断
if klu.rsi > 70:
    print("RSI超买")
elif klu.rsi < 30:
    print("RSI超卖")

# 布林线位置
if klu.close > klu.boll.UP:
    print("突破布林上轨")
elif klu.close < klu.boll.DOWN:
    print("跌破布林下轨")
```

---

## 下一步

- [通用模块](./09-common.md) - 工具函数和枚举
- [配置详解](../05-configuration/01-chan-config.md) - 更多配置选项


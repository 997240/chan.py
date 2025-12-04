# 买卖点模块 (buy_sell_point)

## 模块概述

`buy_sell_point/` 模块负责形态学买卖点的计算，是缠论交易信号的核心。

---

## 目录结构

```
buy_sell_point/
├── __init__.py
├── bs_point.py          # 买卖点类
├── bs_point_list.py     # 买卖点列表
└── bs_point_config.py   # 买卖点配置
```

---

## 买卖点类型

### 概览

| 类型 | 配置值 | 说明 |
|------|--------|------|
| 一类 | "1" | 趋势背驰点 |
| 盘整背驰 | "1p" | 盘整走势背驰 |
| 二类 | "2" | 一类后第一次回调 |
| 类二 | "2s" | 二类后类似结构 |
| 三类A | "3a" | 中枢在一类后面 |
| 三类B | "3b" | 中枢在一类前面 |

### 一类买卖点 (T1)

在趋势末端，最后一个中枢之后出现背驰：

```
一类买点示意:

    ●
   / \        中枢
  /   \    ┌───────┐
 ●     \   │       │
        \  │       │
         ● │       │
          \│       │
           ●───────● ← 背驰，一买
```

条件：
- 至少经历 `min_zs_cnt` 个中枢
- 离开中枢的笔相对进入的笔有背驰 (`divergence_rate`)
- 买点是整个走势最低点 (`bs1_peak`)

### 二类买卖点 (T2)

一类买卖点后的第一次回调：

```
        ●
       /
      / ← 二买
     ●
    / 
   ●  ← 一买
```

条件：
- 必须跟在一类后面 (`bsp2_follow_1`)
- 回调幅度不超过 `max_bs2_rate`

### 三类买卖点 (T3)

离开中枢后的回调不进入中枢：

```
          ●
         /
        / ← 三买
   ┌───●───┐
   │  中枢  │
   └───────┘
```

---

## BSPoint 类

### 主要属性

```python
class BSPoint:
    bi: Bi                # 对应的笔
    is_buy: bool          # 是否买点
    type: BSP_TYPE        # 买卖点类型
    relate_bsp1: BSPoint  # 关联的一类买卖点
```

### BSP_TYPE 枚举

```python
class BSP_TYPE(Enum):
    T1 = '1'      # 一类
    T1P = '1p'    # 盘整背驰
    T2 = '2'      # 二类
    T2S = '2s'    # 类二
    T3A = '3a'    # 三类A
    T3B = '3b'    # 三类B
```

---

## 配置参数

### 背驰相关

```python
config = ChanConfig({
    "divergence_rate": 0.9,      # 背驰比例阈值
    "macd_algo": "peak",         # 背驰计算方法
})
```

**macd_algo 选项**:

| 值 | 说明 |
|------|------|
| peak | MACD柱子峰值（默认） |
| area | MACD面积（同向） |
| full_area | MACD完整面积 |
| slope | 笔的斜率 |
| amp | 笔的涨跌幅 |
| diff | MACD差值 |
| volume | 成交量 |
| amount | 成交额 |

### 买卖点条件

```python
config = ChanConfig({
    "min_zs_cnt": 1,             # 一类至少经历的中枢数
    "bs1_peak": True,            # 一类必须是极值点
    "max_bs2_rate": 0.9999,      # 二类最大回撤比例
    "bs_type": "1,1p,2,2s,3a,3b",# 计算哪些类型
})
```

### 依赖关系

```python
config = ChanConfig({
    "bsp2_follow_1": True,       # 二类必须跟在一类后
    "bsp3_follow_1": True,       # 三类必须跟在一类后
    "bsp2s_follow_2": False,     # 类二必须跟在二类后
    "strict_bsp3": False,        # 三类中枢必须紧挨一类
})
```

---

## 使用示例

### 获取买卖点

```python
chan = Chan(...)

# 获取所有买卖点
for bsp in chan[0].bs_point_lst:
    action = "买" if bsp.is_buy else "卖"
    print(f"{bsp.type.value}类{action}点")
    print(f"  笔序号: {bsp.bi.idx}")
    print(f"  价格: {bsp.bi.get_end_val():.2f}")
```

### 筛选特定类型

```python
# 只看一类买点
buy_points_1 = [
    bsp for bsp in chan[0].bs_point_lst 
    if bsp.is_buy and bsp.type == BSP_TYPE.T1
]

print(f"一类买点数量: {len(buy_points_1)}")
```

### 获取最新买卖点

```python
# 获取最近的N个买卖点
latest = chan.get_latest_bsp(number=3)

for bsp in latest:
    print(f"{bsp.type}: {'买' if bsp.is_buy else '卖'}")
```

### 分析买卖点分布

```python
from collections import Counter

# 统计各类型数量
types = [bsp.type for bsp in chan[0].bs_point_lst]
counter = Counter(types)

for bsp_type, count in counter.items():
    print(f"{bsp_type.value}: {count}个")
```

---

## 线段买卖点

线段也可以计算买卖点（更高级别）：

```python
# 线段买卖点使用不同的配置
config = ChanConfig({
    "macd_algo-seg": "slope",    # 线段用斜率算法
})
```

线段买卖点存储在 `seg_bs_point_lst` 中。

---

## 精确配置

可以为买点/卖点、笔/线段分别配置：

```python
config = ChanConfig({
    # 笔的买点
    "min_zs_cnt-buy": 2,
    
    # 笔的卖点
    "min_zs_cnt-sell": 1,
    
    # 线段的买卖点
    "min_zs_cnt-seg": 1,
    
    # 线段的买点
    "min_zs_cnt-segbuy": 2,
})
```

后缀说明：
- `-buy`: 笔买点
- `-sell`: 笔卖点
- `-seg`: 线段买卖点
- `-segbuy`: 线段买点
- `-segsell`: 线段卖点

---

## 注意事项

1. **买卖点是形态学的**：基于历史走势计算，事后看一定正确
2. **实时交易需要策略**：实盘需要自定义策略（cbsp）来判断入场时机
3. **背驰是相对的**：`divergence_rate` 需要根据市场调整

---

## 下一步

- [绘图模块](./07-plot.md) - 可视化买卖点
- [策略买卖点](../07-full-version/02-cbsp-strategy.md) - 完整版的动力学买卖点


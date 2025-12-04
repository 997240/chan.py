# K线模块 (kline)

## 模块概述

`kline/` 模块负责K线的存储、合并和分形识别，是缠论计算的基础。

---

## 目录结构

```
kline/
├── __init__.py
├── kline_list.py     # K线列表，汇总所有缠论元素
├── kline.py          # 合并K线 (KLine/klc)
├── kline_unit.py     # 单根K线 (KLineUnit/klu)
└── trade_info.py     # 交易信息（成交量等）
```

---

## KLineUnit (单根K线)

原始的单根K线数据。

### 主要属性

```python
class KLineUnit:
    idx: int                    # 序号
    time: CTime                 # 时间
    open: float                 # 开盘价
    high: float                 # 最高价
    low: float                  # 最低价
    close: float                # 收盘价
    kl_type: KL_TYPE            # K线类型
    trade_info: TradeInfo       # 交易信息
    macd: MACD                  # MACD指标
    
    # 合并关系
    klc: KLine                  # 所属合并K线
    
    # 多级别关系
    sup_kl: KLineUnit           # 父级别K线
    sub_kl_list: List[KLineUnit]# 子级别K线列表
```

### 创建方式

```python
item_dict = {
    DATA_FIELD.FIELD_TIME: CTime(2023, 1, 3, 0, 0),
    DATA_FIELD.FIELD_OPEN: 10.0,
    DATA_FIELD.FIELD_HIGH: 10.5,
    DATA_FIELD.FIELD_LOW: 9.8,
    DATA_FIELD.FIELD_CLOSE: 10.2,
}

klu = KLineUnit(item_dict)
```

---

## KLine (合并K线)

处理了包含关系后的K线，是笔计算的基础。

### 包含关系

当两根K线存在包含关系时需要合并:

```
情况1: 后包含前        情况2: 前包含后

    ┌───┐                 ┌───┐
    │   │ ┌───┐       ┌───┤   │
    │   │ │   │       │   │   │
    │   │ └───┘       └───┤   │
    └───┘                 └───┘
```

### 合并规则

```python
# 上升趋势: 取高的高，取低的高
if dir == KLINE_DIR.UP:
    high = max(k1.high, k2.high)
    low = max(k1.low, k2.low)

# 下降趋势: 取高的低，取低的低  
if dir == KLINE_DIR.DOWN:
    high = min(k1.high, k2.high)
    low = min(k1.low, k2.low)
```

### 主要属性

```python
class KLine:
    idx: int                    # 序号
    lst: List[KLineUnit]        # 包含的原始K线
    high: float                 # 合并后最高价
    low: float                  # 合并后最低价
    fx: FX_TYPE                 # 分形类型
    dir: KLINE_DIR              # 方向
    
    pre: KLine                  # 前一个
    next: KLine                 # 后一个
```

### 分形类型

```python
class FX_TYPE(Enum):
    TOP = auto()      # 顶分形
    BOTTOM = auto()   # 底分形
    UNKNOWN = auto()  # 未知
```

### 分形识别

```
顶分形: 中间最高
     ●
    / \
   ●   ●

底分形: 中间最低
   ●   ●
    \ /
     ●
```

---

## KLineList

K线列表，是级别数据的容器，包含所有缠论元素。

### 主要属性

```python
class KLineList:
    lst: List[KLine]            # 合并K线列表
    bi_list: BiList             # 笔列表
    seg_list: SegList           # 线段列表
    segseg_list: SegList        # 线段的线段
    bs_point_lst: BSPointList   # 买卖点列表
    
    metric_model_lst: List      # 技术指标模型
    conf: ChanConfig            # 配置
```

### 主要方法

```python
# 添加单根K线
kl_list.add_single_klu(klu)

# 计算线段和中枢
kl_list.cal_seg_and_zs()

# 访问数据
kl_list[0]          # 第一个合并K线
kl_list[-1]         # 最后一个合并K线
len(kl_list)        # 合并K线数量
```

### 访问缠论元素

```python
# 通过 Chan 对象访问
chan = Chan(...)

# 获取合并K线
for klc in chan[0]:
    print(klc.high, klc.low, klc.fx)

# 获取笔
for bi in chan[0].bi_list:
    print(bi.dir, bi.get_begin_val(), bi.get_end_val())

# 获取线段
for seg in chan[0].seg_list:
    print(seg.dir, len(seg.zs_lst))

# 获取买卖点
for bsp in chan[0].bs_point_lst:
    print(bsp.type, bsp.is_buy)
```

---

## TradeInfo

交易信息类。

```python
class TradeInfo:
    volume: float          # 成交量
    turnover: float        # 成交额
    turnover_rate: float   # 换手率
```

---

## 技术指标计算

在添加K线时自动计算技术指标:

```python
# 配置指标
config = ChanConfig({
    "mean_metrics": [5, 20],      # 5日、20日均线
    "trend_metrics": [20],        # 20日高低轨
    "boll_n": 20,                 # 布林线
    "cal_demark": True,           # Demark指标
    "cal_rsi": True,              # RSI
    "cal_kdj": True,              # KDJ
})

# 访问指标
klu = chan[0][-1][-1]  # 最后一根K线
print(klu.macd.macd)   # MACD值
print(klu.macd.dea)    # DEA值
print(klu.macd.dif)    # DIF值
```

---

## 使用示例

### 遍历合并K线

```python
chan = Chan(...)

for klc in chan[0]:
    print(f"KLC {klc.idx}: high={klc.high:.2f}, low={klc.low:.2f}")
    print(f"  包含 {len(klc.lst)} 根原始K线")
    print(f"  分形类型: {klc.fx}")
```

### 查看分形

```python
# 只查看有分形的K线
for klc in chan[0]:
    if klc.fx != FX_TYPE.UNKNOWN:
        fx_type = "顶" if klc.fx == FX_TYPE.TOP else "底"
        print(f"KLC {klc.idx}: {fx_type}分形, 价格={klc.high if klc.fx == FX_TYPE.TOP else klc.low:.2f}")
```

---

## 下一步

- [笔模块](./03-bi.md) - 了解笔的计算
- [合并器](../combiner/) - K线合并实现细节


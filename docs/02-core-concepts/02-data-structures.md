# 数据结构

本文档介绍项目中的核心数据结构和类。

---

## 类层次总览

```
Chan (主入口)
├── KLineList (K线列表)
│   ├── KLine (合并K线)
│   │   └── KLineUnit (单根K线)
│   ├── BiList (笔列表)
│   │   └── Bi (笔)
│   ├── SegList (线段列表)
│   │   └── Seg (线段)
│   │       └── ZS (中枢)
│   └── BSPointList (买卖点列表)
│       └── BSPoint (买卖点)
└── ChanConfig (配置)
```

---

## Chan 类

主入口类，负责整体流程控制。

### 创建方式

```python
chan = Chan(
    code="sz.000001",           # 股票代码
    begin_time="2023-01-01",    # 开始时间
    end_time="2023-12-31",      # 结束时间
    data_src=DATA_SRC.BAO_STOCK,# 数据源
    lv_list=[KL_TYPE.K_DAY],    # K线级别列表
    config=ChanConfig({}),      # 配置
    autype=AUTYPE.QFQ,          # 复权类型
)
```

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `code` | str | 股票代码 |
| `lv_list` | List[KL_TYPE] | K线级别列表 |
| `kl_datas` | Dict[KL_TYPE, KLineList] | 各级别数据 |
| `conf` | ChanConfig | 配置对象 |

### 访问数据

```python
# 方式1: 通过索引
chan[0]                    # 第一个级别的KLineList
chan[1]                    # 第二个级别的KLineList

# 方式2: 通过类型
chan[KL_TYPE.K_DAY]        # 日线KLineList
chan[KL_TYPE.K_60M]        # 60分钟KLineList
```

---

## KLineUnit 类

单根原始K线。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | K线序号 |
| `time` | CTime | 时间 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `kl_type` | KL_TYPE | K线类型 |
| `trade_info` | TradeInfo | 交易信息 |
| `macd` | MACD | MACD指标 |
| `klc` | KLine | 所属合并K线 |
| `sup_kl` | KLineUnit | 父级别K线 |
| `sub_kl_list` | List[KLineUnit] | 子级别K线列表 |

---

## KLine 类

合并后的K线（处理了包含关系）。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 序号 |
| `lst` | List[KLineUnit] | 包含的原始K线 |
| `high` | float | 合并后的最高价 |
| `low` | float | 合并后的最低价 |
| `fx` | FX_TYPE | 分形类型 |
| `dir` | KLINE_DIR | 方向 |
| `pre` | KLine | 前一个合并K线 |
| `next` | KLine | 后一个合并K线 |

### 分形类型 (FX_TYPE)

```python
class FX_TYPE(Enum):
    BOTTOM = auto()   # 底分形
    TOP = auto()      # 顶分形
    UNKNOWN = auto()  # 未知
```

---

## Bi 类

笔。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 笔序号 |
| `dir` | BI_DIR | 方向 |
| `begin_klc` | KLine | 起始合并K线 |
| `end_klc` | KLine | 结束合并K线 |
| `is_sure` | bool | 是否确定 |
| `parent_seg` | Seg | 所属线段 |
| `bsp` | BSPoint | 买卖点（如果有） |
| `pre` | Bi | 前一笔 |
| `next` | Bi | 后一笔 |

### 主要方法

```python
bi.is_up()          # 是否上升笔
bi.is_down()        # 是否下降笔
bi.get_begin_val()  # 获取起点价格
bi.get_end_val()    # 获取终点价格
bi.amp()            # 笔的振幅
bi.get_klu_cnt()    # 包含的K线数量
```

### 方向类型 (BI_DIR)

```python
class BI_DIR(Enum):
    UP = auto()    # 上升
    DOWN = auto()  # 下降
```

---

## Seg 类

线段。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 线段序号 |
| `dir` | BI_DIR | 方向 |
| `start_bi` | Bi | 起始笔 |
| `end_bi` | Bi | 结束笔 |
| `is_sure` | bool | 是否确定 |
| `zs_lst` | List[ZS] | 中枢列表 |
| `pre` | Seg | 前一线段 |
| `next` | Seg | 后一线段 |

### 主要方法

```python
seg.is_up()           # 是否上升线段
seg.is_down()         # 是否下降线段
seg.get_begin_val()   # 起点价格
seg.get_end_val()     # 终点价格
seg.cal_bi_cnt()      # 包含的笔数量
```

---

## ZS 类

中枢。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `begin` | Bi | 起始笔 |
| `end` | Bi | 结束笔 |
| `high` | float | 中枢高点 (ZG) |
| `low` | float | 中枢低点 (ZD) |
| `peak_high` | float | 最高点 (GG) |
| `peak_low` | float | 最低点 (DD) |
| `bi_in` | Bi | 进入中枢的笔 |
| `bi_out` | Bi | 离开中枢的笔 |
| `bi_lst` | List[Bi] | 中枢内的笔列表 |

### 主要方法

```python
zs.is_up()      # 是否上升中枢
zs.is_down()    # 是否下降中枢
zs.in_range(v)  # 价格是否在中枢范围内
```

---

## BSPoint 类

形态学买卖点。

### 主要属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `bi` | Bi | 对应的笔 |
| `is_buy` | bool | 是否买点 |
| `type` | BSP_TYPE | 买卖点类型 |
| `relate_bsp1` | BSPoint | 关联的一类买卖点 |

### 买卖点类型 (BSP_TYPE)

```python
class BSP_TYPE(Enum):
    T1 = '1'    # 一类买卖点
    T1P = '1p'  # 盘整背驰
    T2 = '2'    # 二类买卖点
    T2S = '2s'  # 类二买卖点
    T3A = '3a'  # 三类（中枢在1类后）
    T3B = '3b'  # 三类（中枢在1类前）
```

---

## ChanConfig 类

配置类。

### 创建方式

```python
config = ChanConfig({
    "bi_strict": True,
    "seg_algo": "chan",
    "zs_combine": True,
    # ... 更多配置
})
```

### 子配置

| 属性 | 类型 | 说明 |
|------|------|------|
| `bi_conf` | BiConfig | 笔配置 |
| `seg_conf` | SegConfig | 线段配置 |
| `zs_conf` | ZSConfig | 中枢配置 |
| `bs_point_conf` | BSPointConfig | 买卖点配置 |

详细配置说明见 [ChanConfig详解](../05-configuration/01-chan-config.md)

---

## 枚举类型汇总

### KL_TYPE (K线类型)

```python
class KL_TYPE(Enum):
    K_1M = auto()       # 1分钟
    K_3M = auto()       # 3分钟
    K_5M = auto()       # 5分钟
    K_15M = auto()      # 15分钟
    K_30M = auto()      # 30分钟
    K_60M = auto()      # 60分钟
    K_DAY = auto()      # 日线
    K_WEEK = auto()     # 周线
    K_MON = auto()      # 月线
    K_QUARTER = auto()  # 季线
    K_YEAR = auto()     # 年线
```

### DATA_SRC (数据源)

```python
class DATA_SRC(Enum):
    BAO_STOCK = auto()  # BaoStock
    CSV = auto()        # CSV文件
    FUTU = auto()       # 富途
    CCXT = auto()       # 数字货币
```

### AUTYPE (复权类型)

```python
class AUTYPE(Enum):
    QFQ = auto()   # 前复权
    HFQ = auto()   # 后复权
    NONE = auto()  # 不复权
```

---

## 下一步

- [整体架构](../03-architecture/01-overview.md) - 了解系统架构
- [模块详解](../04-modules/) - 深入各个模块


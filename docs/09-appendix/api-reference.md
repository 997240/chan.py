# API 速查

## Chan 类

主入口类。

### 构造函数

```python
Chan(
    code: str,                    # 股票代码
    begin_time: str = None,       # 开始时间 "YYYY-MM-DD"
    end_time: str = None,         # 结束时间
    data_src: DATA_SRC = DATA_SRC.BAO_STOCK,  # 数据源
    lv_list: List[KL_TYPE] = None,  # K线级别列表
    config: ChanConfig = None,    # 配置
    autype: AUTYPE = AUTYPE.QFQ,  # 复权类型
)
```

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `chan[n]` | KLineList | 获取第n个级别的数据 |
| `chan[KL_TYPE.K_DAY]` | KLineList | 按类型获取数据 |
| `get_latest_bsp(number=1)` | List[BSPoint] | 获取最新N个买卖点 |
| `chan_dump_pickle(path)` | None | 序列化保存 |
| `Chan.chan_load_pickle(path)` | Chan | 反序列化加载 |

---

## ChanConfig 类

配置类。

### 构造函数

```python
ChanConfig(conf: dict = None)
```

### 常用配置

```python
{
    # 笔配置
    "bi_algo": "normal",       # normal/fx
    "bi_strict": True,
    "bi_fx_check": "strict",   # strict/loss/half/totally
    
    # 线段配置
    "seg_algo": "chan",        # chan/break/1+1
    "left_seg_method": "peak", # all/peak
    
    # 中枢配置
    "zs_combine": True,
    "zs_combine_mode": "zs",   # zs/peak
    "zs_algo": "normal",       # normal/over_seg/auto
    
    # 买卖点配置
    "divergence_rate": 0.9,
    "min_zs_cnt": 1,
    "max_bs2_rate": 0.9999,
    "bs_type": "1,1p,2,2s,3a,3b",
    
    # 技术指标
    "mean_metrics": [],
    "trend_metrics": [],
    "boll_n": 20,
    
    # 回放
    "trigger_step": False,
    "skip_step": 0,
}
```

---

## KLineList 类

K线列表。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `lst` | List[KLine] | 合并K线列表 |
| `bi_list` | BiList | 笔列表 |
| `seg_list` | SegList | 线段列表 |
| `bs_point_lst` | BSPointList | 买卖点列表 |

### 方法

| 方法 | 说明 |
|------|------|
| `kl_list[n]` | 获取第n个合并K线 |
| `len(kl_list)` | 合并K线数量 |
| `for klc in kl_list` | 遍历合并K线 |

---

## KLine 类

合并K线。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 序号 |
| `lst` | List[KLineUnit] | 原始K线列表 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `fx` | FX_TYPE | 分形类型 |
| `dir` | KLINE_DIR | 方向 |
| `pre` | KLine | 前一个 |
| `next` | KLine | 后一个 |

---

## KLineUnit 类

单根K线。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 序号 |
| `time` | CTime | 时间 |
| `open` | float | 开盘价 |
| `high` | float | 最高价 |
| `low` | float | 最低价 |
| `close` | float | 收盘价 |
| `macd` | MACD | MACD指标 |
| `klc` | KLine | 所属合并K线 |

---

## Bi 类

笔。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 序号 |
| `dir` | BI_DIR | 方向 |
| `begin_klc` | KLine | 起始K线 |
| `end_klc` | KLine | 结束K线 |
| `is_sure` | bool | 是否确定 |
| `parent_seg` | Seg | 所属线段 |
| `bsp` | BSPoint | 买卖点 |
| `pre` | Bi | 前一笔 |
| `next` | Bi | 后一笔 |

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `is_up()` | bool | 是否上升笔 |
| `is_down()` | bool | 是否下降笔 |
| `get_begin_val()` | float | 起点价格 |
| `get_end_val()` | float | 终点价格 |
| `get_begin_klu()` | KLineUnit | 起点K线 |
| `get_end_klu()` | KLineUnit | 终点K线 |
| `amp()` | float | 振幅 |
| `get_klu_cnt()` | int | K线数量 |
| `cal_macd_metric(algo, is_reverse)` | float | MACD指标 |

---

## Seg 类

线段。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `idx` | int | 序号 |
| `dir` | BI_DIR | 方向 |
| `start_bi` | Bi | 起始笔 |
| `end_bi` | Bi | 结束笔 |
| `is_sure` | bool | 是否确定 |
| `zs_lst` | List[ZS] | 中枢列表 |
| `pre` | Seg | 前一线段 |
| `next` | Seg | 后一线段 |

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `is_up()` | bool | 是否上升 |
| `is_down()` | bool | 是否下降 |
| `get_begin_val()` | float | 起点价格 |
| `get_end_val()` | float | 终点价格 |
| `cal_bi_cnt()` | int | 笔数量 |

---

## ZS 类

中枢。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `begin` | Bi | 起始笔 |
| `end` | Bi | 结束笔 |
| `high` | float | 中枢高点 |
| `low` | float | 中枢低点 |
| `peak_high` | float | 最高点 |
| `peak_low` | float | 最低点 |
| `bi_in` | Bi | 进入笔 |
| `bi_out` | Bi | 离开笔 |
| `bi_lst` | List[Bi] | 笔列表 |

### 方法

| 方法 | 返回值 | 说明 |
|------|--------|------|
| `is_up()` | bool | 是否上升中枢 |
| `is_down()` | bool | 是否下降中枢 |
| `in_range(value)` | bool | 价格是否在中枢内 |

---

## BSPoint 类

买卖点。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `bi` | Bi | 对应的笔 |
| `is_buy` | bool | 是否买点 |
| `type` | BSP_TYPE | 买卖点类型 |
| `relate_bsp1` | BSPoint | 关联的一类买卖点 |

---

## PlotDriver 类

绑图驱动。

### 构造函数

```python
PlotDriver(
    chan: Chan,
    plot_config: dict = None,
    plot_para: dict = None,
)
```

### 方法

| 方法 | 说明 |
|------|------|
| `figure.show()` | 显示图表 |
| `save2img(path)` | 保存图片 |

---

## 枚举类型速查

### KL_TYPE

```
K_1M, K_3M, K_5M, K_15M, K_30M, K_60M
K_DAY, K_WEEK, K_MON, K_QUARTER, K_YEAR
```

### DATA_SRC

```
BAO_STOCK, CSV, FUTU, CCXT
```

### BI_DIR

```
UP, DOWN
```

### FX_TYPE

```
TOP, BOTTOM, UNKNOWN
```

### BSP_TYPE

```
T1, T1P, T2, T2S, T3A, T3B
```

### AUTYPE

```
QFQ, HFQ, NONE
```

---

## 下一步

- [术语表](./glossary.md) - 专业术语


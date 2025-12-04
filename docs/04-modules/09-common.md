# 通用模块 (common)

## 模块概述

`common/` 模块提供项目中使用的通用工具、枚举和异常类。

---

## 目录结构

```
common/
├── __init__.py
├── enums.py           # 枚举定义
├── chan_exception.py  # 异常类
├── ctime.py           # 时间类
├── cache.py           # 缓存装饰器
└── func_util.py       # 工具函数
```

---

## 枚举类 (enums.py)

### DATA_SRC (数据源)

```python
class DATA_SRC(Enum):
    BAO_STOCK = auto()  # BaoStock (A股)
    CSV = auto()        # CSV文件
    FUTU = auto()       # 富途
    CCXT = auto()       # 数字货币
```

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

### KLINE_DIR (K线方向)

```python
class KLINE_DIR(Enum):
    UP = auto()         # 上升
    DOWN = auto()       # 下降
    COMBINE = auto()    # 合并中
    INCLUDED = auto()   # 被包含
```

### FX_TYPE (分形类型)

```python
class FX_TYPE(Enum):
    BOTTOM = auto()     # 底分形
    TOP = auto()        # 顶分形
    UNKNOWN = auto()    # 未知
```

### BI_DIR (笔方向)

```python
class BI_DIR(Enum):
    UP = auto()         # 上升
    DOWN = auto()       # 下降
```

### BSP_TYPE (买卖点类型)

```python
class BSP_TYPE(Enum):
    T1 = '1'            # 一类
    T1P = '1p'          # 盘整背驰
    T2 = '2'            # 二类
    T2S = '2s'          # 类二
    T3A = '3a'          # 三类A
    T3B = '3b'          # 三类B
```

### AUTYPE (复权类型)

```python
class AUTYPE(Enum):
    QFQ = auto()        # 前复权
    HFQ = auto()        # 后复权
    NONE = auto()       # 不复权
```

### MACD_ALGO (MACD算法)

```python
class MACD_ALGO(Enum):
    AREA = auto()       # 面积
    PEAK = auto()       # 峰值
    FULL_AREA = auto()  # 完整面积
    DIFF = auto()       # 差值
    SLOPE = auto()      # 斜率
    AMP = auto()        # 涨跌幅
    VOLUME = auto()     # 成交量
    AMOUNT = auto()     # 成交额
    # ...
```

### DATA_FIELD (数据字段)

```python
class DATA_FIELD:
    FIELD_TIME = "time_key"
    FIELD_OPEN = "open"
    FIELD_HIGH = "high"
    FIELD_LOW = "low"
    FIELD_CLOSE = "close"
    FIELD_VOLUME = "volume"
    FIELD_TURNOVER = "turnover"
    FIELD_TURNRATE = "turnover_rate"
```

---

## 异常类 (chan_exception.py)

### ChanException

```python
class ChanException(Exception):
    def __init__(self, message, errcode):
        self.errcode = errcode
        super().__init__(message)
```

### 错误码 (ErrCode)

```python
class ErrCode(Enum):
    COMMON_ERROR = auto()
    SRC_DATA_NOT_FOUND = auto()
    SRC_DATA_TYPE_ERR = auto()
    PARA_ERROR = auto()
    CONFIG_ERROR = auto()
    KL_NOT_MONOTONOUS = auto()
    KL_TIME_INCONSISTENT = auto()
    KL_DATA_NOT_ALIGN = auto()
    BI_ERR = auto()
    SEG_ERR = auto()
    ZS_ERR = auto()
    NO_DATA = auto()
```

### 使用示例

```python
from common.chan_exception import ChanException, ErrCode

try:
    chan = Chan(...)
except ChanException as e:
    if e.errcode == ErrCode.NO_DATA:
        print("没有数据")
    elif e.errcode == ErrCode.PARA_ERROR:
        print("参数错误")
    else:
        print(f"错误: {e}")
```

---

## 时间类 (ctime.py)

### CTime

缠论专用时间类，支持多级别时间对齐。

```python
from common.ctime import CTime

# 创建时间
t = CTime(2023, 6, 15, 10, 30)

# 比较
t1 > t2
t1 == t2

# 转字符串
str(t)  # "2023-06-15 10:30"
```

---

## 缓存装饰器 (cache.py)

### @make_cache

用于缓存计算结果，提高性能。

```python
from common.cache import make_cache

class Bi:
    @make_cache
    def get_begin_val(self):
        # 只计算一次，后续从缓存返回
        return self.begin_klc.low if self.is_up() else self.begin_klc.high
```

清除缓存：

```python
bi.clean_cache()  # 数据更新后需要清除缓存
```

---

## 工具函数 (func_util.py)

### check_kltype_order

检查K线级别顺序：

```python
from common.func_util import check_kltype_order

lv_list = [KL_TYPE.K_DAY, KL_TYPE.K_60M]
check_kltype_order(lv_list)  # 从大到小，正确
```

### kltype_lte_day

判断是否是日线及以下级别：

```python
from common.func_util import kltype_lte_day

kltype_lte_day(KL_TYPE.K_DAY)   # True
kltype_lte_day(KL_TYPE.K_60M)  # True
kltype_lte_day(KL_TYPE.K_WEEK) # False
```

### has_overlap

判断两个区间是否有重叠：

```python
from common.func_util import has_overlap

# (low1, high1, low2, high2, equal=是否相等也算重叠)
has_overlap(10, 20, 15, 25)  # True
has_overlap(10, 20, 21, 30)  # False
```

---

## 使用示例

### 枚举使用

```python
from common.enums import KL_TYPE, BI_DIR, BSP_TYPE

# K线类型
if kl_type == KL_TYPE.K_DAY:
    print("日线")

# 笔方向
if bi.dir == BI_DIR.UP:
    print("上升笔")

# 买卖点类型
if bsp.type == BSP_TYPE.T1:
    print("一类买卖点")
```

### 异常处理

```python
from common.chan_exception import ChanException, ErrCode

try:
    chan = Chan(
        code="invalid_code",
        data_src=DATA_SRC.BAO_STOCK,
        ...
    )
except ChanException as e:
    print(f"错误码: {e.errcode}")
    print(f"错误信息: {e}")
```

---

## 下一步

- [配置详解](../05-configuration/01-chan-config.md) - 完整配置说明
- [开发指南](../06-development/) - 开发扩展


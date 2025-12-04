# 数据接入模块 (data_api)

## 模块概述

`data_api/` 模块负责从各种数据源获取K线数据，是系统的数据入口。

---

## 目录结构

```
data_api/
├── __init__.py
├── common_stock_api.py    # 抽象基类
├── bao_stock_api.py       # BaoStock数据源 (A股)
├── csv_api.py             # CSV本地文件
├── ccxt.py                # CCXT数字货币
├── futu_api.py            # 富途API
└── snapshot_api/          # 实时数据接口
    ├── comm_snapshot.py
    ├── futu_snapshot.py
    └── stock_snapshot_api.py
```

---

## 核心类: CommonStockApi

所有数据源的抽象基类。

```python
class CommonStockApi:
    def __init__(self, code, k_type, begin_date, end_date, autype):
        self.code = code
        self.k_type = k_type
        self.begin_date = begin_date
        self.end_date = end_date
        self.autype = autype

    def get_kl_data(self):
        """
        生成器方法，yield返回每根K线
        子类必须实现
        """
        raise NotImplementedError

    @classmethod
    def do_init(cls):
        """初始化连接（如登录）"""
        pass

    @classmethod
    def do_close(cls):
        """关闭连接"""
        pass
```

---

## 已实现的数据源

### 1. BaoStock (A股)

适用于A股历史数据，免费且稳定。

```python
from common.enums import DATA_SRC

chan = Chan(
    code="sz.000001",  # 代码格式: sz.XXXXXX 或 sh.XXXXXX
    data_src=DATA_SRC.BAO_STOCK,
    ...
)
```

**代码格式**:
- 深圳: `sz.000001`
- 上海: `sh.600000`

**支持的K线类型**:
- 日线、周线、月线
- 5/15/30/60分钟

### 2. CSV (本地文件)

从本地CSV文件读取数据。

```python
chan = Chan(
    code="./data/my_stock.csv",  # CSV文件路径
    data_src=DATA_SRC.CSV,
    ...
)
```

**CSV格式要求**:

```csv
time_key,open,high,low,close,volume,turnover,turnover_rate
2023-01-03,10.00,10.50,9.80,10.20,1000000,10000000,0.5
```

| 列名 | 必须 | 说明 |
|------|------|------|
| time_key | ✅ | 时间 |
| open | ✅ | 开盘价 |
| high | ✅ | 最高价 |
| low | ✅ | 最低价 |
| close | ✅ | 收盘价 |
| volume | ❌ | 成交量 |
| turnover | ❌ | 成交额 |
| turnover_rate | ❌ | 换手率 |

### 3. CCXT (数字货币)

支持各大交易所。

```python
chan = Chan(
    code="BTC/USDT",
    data_src=DATA_SRC.CCXT,
    ...
)
```

需要安装: `pip install ccxt`

### 4. Futu (港美股)

富途牛牛API。

```python
chan = Chan(
    code="HK.00700",  # 腾讯
    data_src=DATA_SRC.FUTU,
    ...
)
```

**代码格式**:
- 港股: `HK.00700`
- 美股: `US.AAPL`

需要:
1. 安装: `pip install futu-api`
2. 运行 FutuOpenD 客户端

---

## 返回的数据格式

所有数据源最终返回 `KLineUnit` 对象:

```python
item_dict = {
    DATA_FIELD.FIELD_TIME: CTime(...),     # 时间
    DATA_FIELD.FIELD_OPEN: 10.0,           # 开盘价
    DATA_FIELD.FIELD_HIGH: 10.5,           # 最高价
    DATA_FIELD.FIELD_LOW: 9.8,             # 最低价
    DATA_FIELD.FIELD_CLOSE: 10.2,          # 收盘价
    DATA_FIELD.FIELD_VOLUME: 1000000,      # 成交量
    DATA_FIELD.FIELD_TURNOVER: 10000000,   # 成交额
    DATA_FIELD.FIELD_TURNRATE: 0.5,        # 换手率
}

klu = KLineUnit(item_dict)
```

---

## 使用自定义数据源

通过字符串指定自定义数据源类:

```python
chan = Chan(
    code="...",
    data_src="custom:my_module.MyDataApi",
    ...
)
```

系统会自动导入 `data_api/my_module.py` 中的 `MyDataApi` 类。

详细开发指南见 [自定义数据源](../06-development/01-custom-data-source.md)

---

## 常见问题

### BaoStock 登录失败

```python
import baostock as bs
lg = bs.login()
print(lg.error_code, lg.error_msg)
```

可能原因:
- 非交易时间
- 网络问题

### CSV 时间格式错误

确保时间格式为:
- `YYYY-MM-DD` (日线)
- `YYYY-MM-DD HH:MM:SS` (分钟线)

---

## 下一步

- [K线模块](./02-kline.md) - 了解K线处理
- [自定义数据源](../06-development/01-custom-data-source.md) - 开发新数据源


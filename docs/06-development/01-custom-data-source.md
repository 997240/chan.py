# 自定义数据源

## 概述

本文档介绍如何开发自定义数据源，接入新的数据提供商或本地数据。

---

## 开发步骤

### 1. 创建数据源类

在 `data_api/` 目录下创建新文件：

```python
# data_api/my_data_api.py

from typing import Iterator
from common.ctime import CTime
from common.enums import DATA_FIELD, KL_TYPE
from data_api.common_stock_api import CommonStockApi
from kline.kline_unit import KLineUnit


class MyDataApi(CommonStockApi):
    """自定义数据源"""
    
    def __init__(self, code, k_type, begin_date, end_date, autype):
        super().__init__(code, k_type, begin_date, end_date, autype)
        # 初始化连接等
    
    def get_kl_data(self) -> Iterator[KLineUnit]:
        """
        获取K线数据的生成器
        必须实现此方法
        """
        # 从你的数据源获取数据
        raw_data = self._fetch_data()
        
        for idx, row in enumerate(raw_data):
            item_dict = {
                DATA_FIELD.FIELD_TIME: CTime(
                    row['year'], row['month'], row['day'],
                    row.get('hour', 0), row.get('minute', 0)
                ),
                DATA_FIELD.FIELD_OPEN: float(row['open']),
                DATA_FIELD.FIELD_HIGH: float(row['high']),
                DATA_FIELD.FIELD_LOW: float(row['low']),
                DATA_FIELD.FIELD_CLOSE: float(row['close']),
                DATA_FIELD.FIELD_VOLUME: float(row.get('volume', 0)),
                DATA_FIELD.FIELD_TURNOVER: float(row.get('turnover', 0)),
                DATA_FIELD.FIELD_TURNRATE: float(row.get('turnover_rate', 0)),
            }
            
            yield KLineUnit(item_dict)
    
    def _fetch_data(self):
        """从数据源获取原始数据"""
        # 实现你的数据获取逻辑
        pass
    
    @classmethod
    def do_init(cls):
        """初始化（如登录）"""
        pass
    
    @classmethod
    def do_close(cls):
        """关闭连接"""
        pass
```

---

### 2. 返回数据格式

`get_kl_data()` 必须 yield `KLineUnit` 对象，包含以下字段：

| 字段 | 必须 | 类型 | 说明 |
|------|------|------|------|
| FIELD_TIME | ✅ | CTime | 时间 |
| FIELD_OPEN | ✅ | float | 开盘价 |
| FIELD_HIGH | ✅ | float | 最高价 |
| FIELD_LOW | ✅ | float | 最低价 |
| FIELD_CLOSE | ✅ | float | 收盘价 |
| FIELD_VOLUME | ❌ | float | 成交量 |
| FIELD_TURNOVER | ❌ | float | 成交额 |
| FIELD_TURNRATE | ❌ | float | 换手率 |

---

### 3. CTime 时间类

```python
from common.ctime import CTime

# 日线时间（只有日期）
time = CTime(2023, 6, 15, 0, 0)

# 分钟线时间（包含时分）
time = CTime(2023, 6, 15, 10, 30)

# 从字符串解析
# 需要自己实现解析逻辑
def parse_time(time_str):
    # "2023-06-15 10:30:00"
    parts = time_str.split()
    date_parts = parts[0].split('-')
    time_parts = parts[1].split(':') if len(parts) > 1 else [0, 0]
    
    return CTime(
        int(date_parts[0]),  # year
        int(date_parts[1]),  # month
        int(date_parts[2]),  # day
        int(time_parts[0]),  # hour
        int(time_parts[1]),  # minute
    )
```

---

### 4. 使用自定义数据源

**方式一**: 直接导入

```python
from data_api.my_data_api import MyDataApi

# 需要修改 Chan 类或手动调用
```

**方式二**: 字符串指定（推荐）

```python
chan = Chan(
    code="your_code",
    data_src="custom:my_data_api.MyDataApi",
    ...
)
```

格式: `custom:模块名.类名`

系统会自动执行:
```python
from data_api.my_data_api import MyDataApi
```

---

## 完整示例: MySQL数据源

```python
# data_api/mysql_api.py

import mysql.connector
from typing import Iterator
from common.ctime import CTime
from common.enums import DATA_FIELD, KL_TYPE
from data_api.common_stock_api import CommonStockApi
from kline.kline_unit import KLineUnit


class MySQLDataApi(CommonStockApi):
    """MySQL数据源"""
    
    _conn = None
    
    def __init__(self, code, k_type, begin_date, end_date, autype):
        super().__init__(code, k_type, begin_date, end_date, autype)
        self.table = self._get_table_name(k_type)
    
    def _get_table_name(self, k_type):
        """根据K线类型获取表名"""
        mapping = {
            KL_TYPE.K_DAY: "kline_day",
            KL_TYPE.K_60M: "kline_60m",
            KL_TYPE.K_30M: "kline_30m",
        }
        return mapping.get(k_type, "kline_day")
    
    def get_kl_data(self) -> Iterator[KLineUnit]:
        cursor = self._conn.cursor(dictionary=True)
        
        sql = f"""
            SELECT * FROM {self.table}
            WHERE code = %s
            AND trade_date >= %s
            AND trade_date <= %s
            ORDER BY trade_date ASC
        """
        
        cursor.execute(sql, (self.code, self.begin_date, self.end_date))
        
        for row in cursor:
            dt = row['trade_date']
            time = CTime(dt.year, dt.month, dt.day, 0, 0)
            
            item_dict = {
                DATA_FIELD.FIELD_TIME: time,
                DATA_FIELD.FIELD_OPEN: float(row['open']),
                DATA_FIELD.FIELD_HIGH: float(row['high']),
                DATA_FIELD.FIELD_LOW: float(row['low']),
                DATA_FIELD.FIELD_CLOSE: float(row['close']),
                DATA_FIELD.FIELD_VOLUME: float(row['volume']),
            }
            
            yield KLineUnit(item_dict)
        
        cursor.close()
    
    @classmethod
    def do_init(cls):
        """初始化数据库连接"""
        cls._conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="stock"
        )
    
    @classmethod
    def do_close(cls):
        """关闭连接"""
        if cls._conn:
            cls._conn.close()
            cls._conn = None
```

使用:

```python
chan = Chan(
    code="000001",
    data_src="custom:mysql_api.MySQLDataApi",
    begin_time="2023-01-01",
    end_time="2023-12-31",
    lv_list=[KL_TYPE.K_DAY],
    ...
)
```

---

## 注意事项

1. **时间顺序**: K线必须按时间升序返回
2. **时间唯一**: 每个时间点只能有一根K线
3. **数据完整**: 尽量提供完整的OHLCV数据
4. **异常处理**: 数据获取失败时抛出 `ChanException`

```python
from common.chan_exception import ChanException, ErrCode

if not data:
    raise ChanException("无法获取数据", ErrCode.SRC_DATA_NOT_FOUND)
```

---

## 下一步

- [自定义笔算法](./02-custom-bi-algo.md) - 开发笔算法
- [自定义线段算法](./03-custom-seg-algo.md) - 开发线段算法


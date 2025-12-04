# 数据库系统

## 概述

完整版支持 MySQL 和 SQLite 两种数据库后端，用于存储交易信号和记录。

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                      数据库架构                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CChanDB (统一接口)                     │   │
│  │  - add_signal()      添加信号                           │   │
│  │  - get_signals()     获取信号                           │   │
│  │  - update_trade()    更新交易                           │   │
│  │  - get_positions()   获取持仓                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│            ┌───────────────┴───────────────┐                   │
│            ▼                               ▼                   │
│  ┌─────────────────────┐       ┌─────────────────────┐        │
│  │     MysqlDB         │       │     SqliteDB        │        │
│  │  - 生产环境         │       │  - 开发/测试        │        │
│  │  - 高并发           │       │  - 单机部署         │        │
│  └─────────────────────┘       └─────────────────────┘        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 配置

### config.yaml

```yaml
DB:
  TYPE: mysql              # mysql 或 sqlite
  
  # MySQL 配置
  HOST: 127.0.0.1
  PORT: 3306
  USER: root
  PASSWD: password
  DATABASE: chan_trade
  
  # SQLite 配置
  SQLITE_PATH: ./data/trade.db
  TABLE: trade_record
```

---

## 数据表

### trade_record (交易记录表)

```sql
CREATE TABLE trade_record (
    -- 基础信息
    id INT AUTO_INCREMENT PRIMARY KEY,
    add_date DATETIME(6),            -- 信号添加时间
    stock_code VARCHAR(20) NOT NULL, -- 股票代码
    stock_name VARCHAR(64) NOT NULL, -- 股票名称
    status VARCHAR(20) NOT NULL,     -- 状态
    lv CHAR(5) NOT NULL,             -- K线级别
    bstype CHAR(10) NOT NULL,        -- 买卖点类型
    is_buy BOOLEAN DEFAULT TRUE,     -- 是否买入
    
    -- 信号信息
    open_thred FLOAT,                -- 开仓阈值
    sl_thred FLOAT,                  -- 止损阈值
    target_klu_time VARCHAR(10),     -- 目标K线时间
    watching BOOLEAN DEFAULT TRUE,   -- 是否监控中
    unwatch_reason VARCHAR(256),     -- 取消监控原因
    signal_last_modify DATETIME(6),  -- 信号最后修改时间
    
    -- 模型信息
    model_version VARCHAR(256),      -- 模型版本
    model_score_before FLOAT,        -- 开仓前分数
    model_score_after FLOAT,         -- 开仓后分数
    snapshot_before VARCHAR(256),    -- 开仓前快照
    snapshot_after VARCHAR(256),     -- 开仓后快照
    
    -- 开仓信息
    is_open BOOLEAN DEFAULT FALSE,   -- 是否已开仓
    open_price FLOAT,                -- 开仓价格
    quota INT DEFAULT 0,             -- 开仓数量
    open_date DATETIME(6),           -- 开仓时间
    open_order_id VARCHAR(32),       -- 开仓订单ID
    open_image_url VARCHAR(64),      -- 开仓截图URL
    peak_price_after_open FLOAT,     -- 开仓后峰值价格
    
    -- 平仓信息
    cover_avg_price FLOAT,           -- 平仓均价
    cover_quota INT DEFAULT 0,       -- 平仓数量
    cover_date DATETIME(6),          -- 平仓时间
    cover_reason VARCHAR(256),       -- 平仓原因
    cover_order_id VARCHAR(256),     -- 平仓订单ID
    cover_image_url VARCHAR(64),     -- 平仓截图URL
    
    -- 错误标记
    open_err BOOLEAN DEFAULT FALSE,  -- 开仓错误
    close_err BOOLEAN DEFAULT FALSE, -- 平仓错误
    open_err_reason VARCHAR(256),    -- 开仓错误原因
    close_err_reason VARCHAR(256),   -- 平仓错误原因
    
    -- 关联信息
    relate_cover_id INT,             -- 关联的平仓记录ID
    is_cover_record BOOLEAN DEFAULT FALSE -- 是否是平仓记录
);
```

---

## CChanDB 接口

### 初始化

```python
from Trade.db_util import CChanDB

# 自动从配置文件读取数据库类型和连接参数
db = CChanDB()
```

### 信号操作

```python
# 添加信号
db.add_signal(
    code="HK.00700",
    name="腾讯控股",
    lv="K_DAY",
    bstype="1",
    is_buy=True,
    open_thred=320.0,
    sl_thred=304.0,
)

# 获取待处理信号
signals = db.get_watching_signals(market="hk")

# 取消监控
db.unwatch_signal(signal_id=123, reason="信号失效")
```

### 交易操作

```python
# 更新开仓信息
db.update_open(
    signal_id=123,
    open_price=318.5,
    quota=100,
    order_id="12345678",
)

# 更新平仓信息
db.update_cover(
    signal_id=123,
    cover_price=340.0,
    cover_quota=100,
    reason="止盈",
)

# 获取持仓
positions = db.get_open_positions(market="hk")
```

### 查询操作

```python
# 获取历史交易
trades = db.get_trade_history(
    begin_date="2023-01-01",
    end_date="2023-12-31",
    market="hk",
)

# 获取单条记录
record = db.get_record_by_id(signal_id=123)
```

---

## 状态流转

```
┌─────────────┐
│   SIGNAL    │  信号已入库
└──────┬──────┘
       │
       ▼ (突破阈值)
┌─────────────┐
│    OPEN     │  已开仓
└──────┬──────┘
       │
       ├────────────────┬────────────────┐
       ▼                ▼                ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  STOP_LOSS  │  │ TAKE_PROFIT │  │   SIGNAL    │
│   止损平仓   │  │   止盈平仓   │  │   信号平仓   │
└─────────────┘  └─────────────┘  └─────────────┘
```

---

## MySQL 部署

### 创建数据库

```sql
CREATE DATABASE chan_trade CHARACTER SET utf8mb4;
```

### 创建用户

```sql
CREATE USER 'chan'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON chan_trade.* TO 'chan'@'localhost';
FLUSH PRIVILEGES;
```

### 初始化表

```python
# Script/InitDB.py
from Trade.db_util import CChanDB

db = CChanDB()
db.init_tables()
```

---

## SQLite 部署

SQLite 无需额外配置，指定文件路径即可：

```yaml
DB:
  TYPE: sqlite
  SQLITE_PATH: ./data/trade.db
  TABLE: trade_record
```

---

## 数据备份

### MySQL 备份

```bash
mysqldump -u root -p chan_trade > backup.sql
```

### SQLite 备份

```bash
cp ./data/trade.db ./backup/trade_$(date +%Y%m%d).db
```

---

## 常用查询

### 统计收益

```sql
SELECT 
    SUM(CASE WHEN is_buy THEN 
        (cover_avg_price - open_price) * quota 
    ELSE 
        (open_price - cover_avg_price) * quota 
    END) as total_profit
FROM trade_record
WHERE is_open = TRUE 
AND cover_avg_price IS NOT NULL;
```

### 统计胜率

```sql
SELECT 
    COUNT(*) as total,
    SUM(CASE WHEN 
        (is_buy AND cover_avg_price > open_price) OR
        (NOT is_buy AND cover_avg_price < open_price)
    THEN 1 ELSE 0 END) as win_count
FROM trade_record
WHERE cover_avg_price IS NOT NULL;
```

---

## 下一步

- [FAQ](../08-faq/faq.md) - 常见问题
- [API速查](../09-appendix/api-reference.md) - 接口参考


# 交易引擎

## 概述

交易引擎对接券商API，实现自动化交易。目前完整版支持对接 Futu（富途）。

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                      交易引擎架构                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    信号监控 (SignalMonitor)               │   │
│  │  - 例行计算交易信号                                      │   │
│  │  - 信号入库                                              │   │
│  │  - 删除失效信号                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    信号数据库 (CChanDB)                   │   │
│  │  - 存储待处理信号                                        │   │
│  │  - 存储已开仓记录                                        │   │
│  │  - 存储平仓记录                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    交易引擎 (CTradeEngine)                │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  开仓流程                                        │    │   │
│  │  │  1. 检查信号是否突破                             │    │   │
│  │  │  2. 获取模型分数                                 │    │   │
│  │  │  3. 检查分数阈值                                 │    │   │
│  │  │  4. 计算仓位                                     │    │   │
│  │  │  5. 提交订单                                     │    │   │
│  │  │  6. 跟踪订单状态                                 │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  │                                                          │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  平仓流程                                        │    │   │
│  │  │  1. 监控持仓                                     │    │   │
│  │  │  2. 检测止损/止盈/信号平仓                       │    │   │
│  │  │  3. 提交平仓单                                   │    │   │
│  │  │  4. 更新数据库                                   │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 券商API (FutuTradeEngine)                 │   │
│  │  - 连接富途OpenD                                         │   │
│  │  - 下单/撤单                                             │   │
│  │  - 查询持仓/订单                                         │   │
│  │  - 获取实时行情                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 核心组件

### 1. CTradeEngine

交易引擎核心类：

```python
class CTradeEngine:
    def __init__(self, market, chan_db):
        self.market = market      # 市场 (港股/美股/A股)
        self.chan_db = chan_db    # 数据库
        self.futu = None          # Futu API
    
    def wait4MarketOpen(self):
        """等待市场开盘"""
        pass
    
    def add_trade(self, trade_info, price):
        """提交开仓单"""
        pass
    
    def close_trade(self, trade_id, price, reason):
        """提交平仓单"""
        pass
    
    def poll_order_status(self):
        """轮询订单状态"""
        pass
```

### 2. FutuTradeEngine

Futu API 封装：

```python
class FutuTradeEngine:
    def __init__(self, host, port):
        self.host = host
        self.port = port
    
    def connect(self):
        """连接OpenD"""
        pass
    
    def place_order(self, code, price, qty, side):
        """下单"""
        pass
    
    def cancel_order(self, order_id):
        """撤单"""
        pass
    
    def get_position(self, code):
        """获取持仓"""
        pass
```

### 3. COpenQuotaGen

仓位管理：

```python
class COpenQuotaGen:
    @classmethod
    def bench_price_func(cls, bench_price):
        """固定金额策略"""
        def f(price, lot_size) -> int:
            quota = lot_size
            while quota * price < bench_price:
                quota += lot_size
            return quota
        return f
```

---

## 交易流程

### 开仓流程

```
1. 信号检测
   │
   ├── 从数据库获取待处理信号
   │
   ├── 获取实时价格
   │
   └── 检查是否突破开仓阈值
       │
       ▼
2. 模型评分
   │
   ├── 计算当前缠论数据
   │
   ├── 获取CBSP特征
   │
   └── 模型预测分数
       │
       ▼
3. 分数过滤
   │
   └── 分数 >= 阈值?
       │
       ├── 否 → 跳过
       │
       └── 是 ↓
       
4. 仓位计算
   │
   └── COpenQuotaGen.calc()
       │
       ▼
5. 提交订单
   │
   ├── FutuTradeEngine.place_order()
   │
   └── 记录到数据库
       │
       ▼
6. 订单跟踪
   │
   ├── 轮询订单状态
   │
   ├── 成交 → 更新数据库
   │
   └── 超时 → 撤单重试
```

### 平仓流程

```
1. 持仓监控
   │
   ├── 从数据库获取持仓
   │
   └── 获取实时价格
       │
       ▼
2. 平仓条件检测
   │
   ├── 止损: 价格 < 止损价
   │
   ├── 止盈: 价格 > 止盈价
   │
   └── 信号平仓: CBSP平仓信号
       │
       ▼
3. 提交平仓单
   │
   └── 更新数据库
```

---

## 配置

### config.yaml

```yaml
Futu:
  PASSWORD_MD5: xxx           # 交易密码MD5
  HOST: 127.0.0.1            # OpenD地址
  PORT: 11111                # OpenD端口
  RSA_PATH: ""               # RSA认证文件
  ENV: SIMULATE              # SIMULATE/REAL

Trade:
  log_file: ./trade.log      # 交易日志
  trade_model_path: ./models # 模型路径
  area: cn,hk,us             # 交易市场
  open_price_tolerance: 0.01 # 价格容差
  open_score_tolerance: 0.03 # 分数容差
  touch_sl_cnt: 1            # 止损确认次数
  touch_sw_cnt: 1            # 止盈确认次数
```

---

## 数据库表结构

```sql
CREATE TABLE trade_record (
    id INT AUTO_INCREMENT PRIMARY KEY,
    add_date DATETIME,           -- 信号时间
    stock_code VARCHAR(20),      -- 股票代码
    stock_name VARCHAR(64),      -- 股票名称
    status VARCHAR(20),          -- 状态
    lv CHAR(5),                  -- K线级别
    bstype CHAR(10),             -- 买卖点类型
    is_buy BOOLEAN,              -- 是否买入
    open_thred FLOAT,            -- 开仓阈值
    sl_thred FLOAT,              -- 止损阈值
    
    -- 开仓信息
    is_open BOOLEAN,             -- 是否已开仓
    open_price FLOAT,            -- 开仓价格
    open_date DATETIME,          -- 开仓时间
    quota INT,                   -- 开仓数量
    
    -- 平仓信息
    cover_avg_price FLOAT,       -- 平仓均价
    cover_date DATETIME,         -- 平仓时间
    cover_reason VARCHAR(256),   -- 平仓原因
    
    -- 模型信息
    model_score_before FLOAT,    -- 开仓前分数
    model_score_after FLOAT,     -- 开仓后分数
);
```

---

## 风控机制

### 1. 开仓检查

- 模型分数阈值
- 交易活跃度检测
- 持仓数量限制

### 2. 止损止盈

- 固定止损率
- 动态止损（跟踪止损）
- 信号止盈

### 3. 异常处理

- 网络断连重试
- 订单超时处理
- 现场恢复

---

## 消息推送

```python
def send_msg(title, content, lv='INFO'):
    """
    发送消息通知
    可对接: gotify/chanify/邮件等
    """
    pass
```

推送内容:
- 开仓成功
- 平仓成功
- 触发止损
- 系统异常

---

## 下一步

- [数据库系统](./06-database.md) - 数据存储
- [FAQ](../08-faq/faq.md) - 常见问题


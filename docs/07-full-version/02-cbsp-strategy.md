# 策略买卖点 (CBSP)

## 概述

CBSP (Custom Buy Sell Point) 是自定义的动力学买卖点，与形态学买卖点 (BSP) 的区别：

| 特性 | BSP (形态学) | CBSP (动力学) |
|------|-------------|---------------|
| 计算时机 | 事后确定 | 实时计算 |
| 准确性 | 一定正确 | 可能有误 |
| 延迟 | 有延迟 | 相对及时 |
| 用途 | 分析学习 | 实际交易 |

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                      CBSP 策略架构                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   CStrategy (抽象基类)                    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  + try_open(chan, lv) → Optional[CCustomBSP]    │    │   │
│  │  │  + try_close(chan, lv) → None                   │    │   │
│  │  │  + bsp_signal(data) → List[CSignal]             │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────┬───────────────────────────────┘   │
│                            │                                    │
│            ┌───────────────┼───────────────┐                   │
│            ▼               ▼               ▼                   │
│  ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐          │
│  │ CCustomStrategy │ │CSegBspStrategy│ │CExamStrategy│         │
│  │   (示例策略)     │ │(线段买卖点)  │ │  (试题生成) │          │
│  └─────────────────┘ └─────────────┘ └─────────────┘          │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CCustomBSP                            │   │
│  │  - bsp: BSPoint (关联的形态学买卖点)                     │   │
│  │  - klu: KLineUnit (触发的K线)                           │   │
│  │  - is_buy: bool (买/卖)                                  │   │
│  │  - open_price: float (开仓价)                           │   │
│  │  - features: Dict (特征)                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    CSignal                               │   │
│  │  - 信号数据，用于信号监控和入库                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 策略接口

### CStrategy 基类

```python
class CStrategy:
    def __init__(self, conf: CChanConfig):
        self.conf = conf
    
    def try_open(self, chan: CChan, lv: int) -> Optional[CCustomBSP]:
        """
        尝试开仓
        
        Args:
            chan: Chan对象，包含所有级别数据
            lv: 当前级别索引
        
        Returns:
            CCustomBSP: 如果应该开仓，返回买卖点信息
            None: 如果不应该开仓
        """
        raise NotImplementedError
    
    def try_close(self, chan: CChan, lv: int) -> None:
        """
        尝试平仓
        
        Args:
            chan: Chan对象
            lv: 当前级别索引
        
        说明:
            如果需要平仓，调用 cbsp.do_close(price, klu, reason)
        """
        raise NotImplementedError
    
    def bsp_signal(self, data: CKLine_List) -> List[CSignal]:
        """
        计算信号（用于信号监控）
        
        Returns:
            符合条件的信号列表
        """
        raise NotImplementedError
```

---

## 策略参数

通过 `CChanConfig` 配置策略：

```python
config = CChanConfig({
    "cbsp_strategy": CCustomStrategy,  # 策略类
    "strategy_para": {
        "strict_open": True,       # 严格开仓
        "use_qjt": True,           # 使用区间套
        "short_shelling": True,    # 允许做空
        "judge_on_close": True,    # 基于收盘价判断
        "max_sl_rate": 0.05,       # 最大止损率
        "max_profit_rate": 0.1,    # 最大止盈率
    },
    "only_judge_last": False,      # 只判断最后一根K线
    "cal_cover": True,             # 计算平仓
})
```

---

## 策略示例

### 简单一类买卖点策略

```python
class SimpleStrategy(CStrategy):
    """
    简单策略：一类买卖点分形确认后开仓
    """
    
    def try_open(self, chan, lv):
        data = chan[lv]
        
        # 检查是否有新的一类买卖点
        if len(data.bs_point_lst) == 0:
            return None
        
        last_bsp = data.bs_point_lst[-1]
        last_klu = data[-1][-1]
        
        # 一类买卖点且是最新的
        if last_bsp.type in [BSP_TYPE.T1, BSP_TYPE.T1P]:
            if last_bsp.bi.end_klc.idx == data[-1].idx:
                return CCustomBSP(
                    bsp=last_bsp,
                    klu=last_klu,
                    is_buy=last_bsp.is_buy,
                    open_price=last_klu.close,
                )
        
        return None
    
    def try_close(self, chan, lv):
        # 简单止损止盈
        for cbsp in chan[lv].cbsp_strategy:
            if cbsp.is_closed:
                continue
            
            current_price = chan[lv][-1][-1].close
            
            # 止损
            if cbsp.is_buy:
                if current_price < cbsp.open_price * 0.95:
                    cbsp.do_close(current_price, chan[lv][-1][-1], "止损")
            else:
                if current_price > cbsp.open_price * 1.05:
                    cbsp.do_close(current_price, chan[lv][-1][-1], "止损")
```

### 区间套策略

```python
class QJTStrategy(CStrategy):
    """
    区间套策略：父级别买卖点 + 子级别一类买卖点
    """
    
    def try_open(self, chan, lv):
        # 必须有子级别
        if lv >= len(chan.lv_list) - 1:
            return None
        
        data = chan[lv]
        sub_data = chan[lv + 1]
        
        # 父级别有买卖点
        if len(data.bs_point_lst) == 0:
            return None
        
        last_bsp = data.bs_point_lst[-1]
        last_klu = data[-1][-1]
        
        # 父级别买卖点在当前K线
        if last_bsp.bi.end_klc.idx != data[-1].idx:
            return None
        
        # 子级别有一类买卖点且在父级别K线内
        for sub_cbsp in sub_data.cbsp_strategy:
            if sub_cbsp.klu.sup_kl.idx == last_klu.idx:
                if sub_cbsp.type.find("1") >= 0:
                    return CCustomBSP(
                        bsp=last_bsp,
                        klu=last_klu,
                        is_buy=last_bsp.is_buy,
                        open_price=sub_cbsp.open_price,
                        bs_type=f"QJT_{last_bsp.type}",
                    )
        
        return None
```

---

## CCustomBSP 类

### 主要属性

```python
class CCustomBSP:
    bsp: BSPoint          # 关联的形态学买卖点
    klu: KLineUnit        # 触发的K线
    is_buy: bool          # 是否买点
    open_price: float     # 开仓价格
    bs_type: str          # 买卖点类型
    
    is_closed: bool       # 是否已平仓
    close_price: float    # 平仓价格
    close_reason: str     # 平仓原因
    
    features: Dict        # 特征字典
    score: float          # 模型分数
```

### 主要方法

```python
# 平仓
cbsp.do_close(price, klu, reason, quota=None)

# 获取收益率
profit = (cbsp.close_price - cbsp.open_price) / cbsp.open_price
```

---

## 信号监控

### CSignal 类

```python
class CSignal:
    code: str             # 股票代码
    lv: KL_TYPE           # K线级别
    is_buy: bool          # 买/卖
    bstype: str           # 买卖点类型
    open_thred: float     # 开仓阈值
    sl_thred: float       # 止损阈值
    target_time: CTime    # 目标时间
```

### 信号流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   信号计算       │ ──▶ │    入库         │ ──▶ │   交易执行       │
│ bsp_signal()    │     │  MySQL/SQLite   │     │  TradeEngine    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

---

## 与公开版的关系

公开版提供了 BSP（形态学买卖点），这是事后分析的基础。

完整版的 CBSP 建立在 BSP 之上：

1. **BSP 提供位置**: 识别可能的买卖点位置
2. **CBSP 提供时机**: 决定何时入场
3. **模型提供评分**: 对 CBSP 进行打分过滤

---

## 下一步

- [机器学习模型](./03-ml-model.md) - 为CBSP评分
- [交易引擎](./05-trade-engine.md) - 执行交易


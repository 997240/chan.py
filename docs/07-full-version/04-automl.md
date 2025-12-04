# AutoML 框架

## 概述

AutoML 用于自动搜索最优的模型参数和交易策略参数。

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                      AutoML 框架架构                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    参数空间定义                           │   │
│  │  - 模型阈值: [0.5, 0.6, 0.7, ...]                       │   │
│  │  - 买卖点类型: ["1", "1,2", "1,2,3", ...]              │   │
│  │  - 止损率: [0.03, 0.05, 0.08, ...]                      │   │
│  │  - 止盈率: [0.05, 0.1, 0.15, ...]                       │   │
│  │  - 其他策略参数                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    搜索算法                               │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │  贝叶斯优化  │ │    PBT     │ │  暴力搜索   │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    策略评估                               │   │
│  │  - 盈亏比                                                │   │
│  │  - 交易次数                                              │   │
│  │  - 最大回撤                                              │   │
│  │  - 平均收益                                              │   │
│  │  - Sharpe比率                                            │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    评分函数                               │   │
│  │  CalScore(eval_res) → float                              │   │
│  │  - 用户自定义评分逻辑                                    │   │
│  │  - 综合考虑收益、风险、交易频率                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    输出最优参数                           │   │
│  │  - 生成配置文件                                          │   │
│  │  - 对接交易引擎                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 搜索参数

### 模型参数

| 参数 | 说明 | 搜索范围 |
|------|------|----------|
| score_thred | 模型分数阈值 | [0.5, 0.9] |
| score_thred_buy | 买点阈值 | [0.5, 0.9] |
| score_thred_sell | 卖点阈值 | [0.5, 0.9] |

### 策略参数

| 参数 | 说明 | 搜索范围 |
|------|------|----------|
| bs_type | 买卖点类型 | ["1", "1,2", "1,2,3a"] |
| max_sl_rate | 最大止损率 | [0.03, 0.1] |
| max_profit_rate | 最大止盈率 | [0.05, 0.2] |
| min_zs_cnt | 最小中枢数 | [1, 3] |

### 过滤参数

| 参数 | 说明 | 搜索范围 |
|------|------|----------|
| market | 市场 | ["cn", "hk", "us"] |
| bsp_type | 买卖点类型过滤 | 各类型组合 |

---

## 搜索算法

### 1. 贝叶斯优化

使用高斯过程模型，根据历史结果预测最优参数：

```python
# 优点: 样本效率高
# 缺点: 计算复杂

from bayes_opt import BayesianOptimization

def objective(score_thred, sl_rate, profit_rate):
    config = create_config(score_thred, sl_rate, profit_rate)
    result = evaluate_strategy(config)
    return CalScore(result)

optimizer = BayesianOptimization(
    f=objective,
    pbounds={
        'score_thred': (0.5, 0.9),
        'sl_rate': (0.03, 0.1),
        'profit_rate': (0.05, 0.2),
    },
)

optimizer.maximize(n_iter=100)
```

### 2. PBT (Population Based Training)

```python
# 优点: 可以并行
# 缺点: 需要更多资源
```

### 3. 暴力搜索

```python
# 优点: 简单直接
# 缺点: 组合爆炸

for score_thred in [0.5, 0.6, 0.7, 0.8]:
    for sl_rate in [0.03, 0.05, 0.08]:
        for profit_rate in [0.05, 0.1, 0.15]:
            config = create_config(...)
            result = evaluate_strategy(config)
            save_result(config, result)
```

---

## 评估指标

### 基础指标

| 指标 | 说明 | 计算方式 |
|------|------|----------|
| win_rate | 胜率 | 盈利次数/总交易次数 |
| profit_loss_ratio | 盈亏比 | 平均盈利/平均亏损 |
| total_return | 总收益 | 所有交易收益之和 |
| max_drawdown | 最大回撤 | 最大净值回撤比例 |
| trade_count | 交易次数 | 总交易次数 |

### 高级指标

| 指标 | 说明 |
|------|------|
| sharpe_ratio | Sharpe比率 |
| calmar_ratio | Calmar比率 |
| sortino_ratio | Sortino比率 |

---

## 评分函数

用户自定义评分逻辑：

```python
def CalScore(eval_res):
    """
    自定义评分函数
    
    Args:
        eval_res: 评估结果字典
    
    Returns:
        综合分数
    """
    # 基础分
    score = 0
    
    # 盈亏比权重
    if eval_res['profit_loss_ratio'] > 1.5:
        score += eval_res['profit_loss_ratio'] * 10
    
    # 胜率权重
    score += eval_res['win_rate'] * 20
    
    # 交易次数惩罚（太少不稳定）
    if eval_res['trade_count'] < 50:
        score *= 0.5
    
    # 回撤惩罚
    score *= (1 - eval_res['max_drawdown'])
    
    return score
```

---

## 使用流程

```
1. 准备数据
   └── 运行回测，生成特征和预测分数

2. 定义参数空间
   └── 设置各参数的搜索范围

3. 选择搜索算法
   └── 贝叶斯/PBT/暴力搜索

4. 定义评分函数
   └── 根据业务需求自定义

5. 运行AutoML
   └── 搜索最优参数

6. 解析结果
   └── 生成配置文件

7. 验证
   └── 在测试集上验证
```

---

## 输出结果

### 结果文件

```yaml
# automl_result.yaml

best_params:
  score_thred: 0.65
  score_thred_buy: 0.7
  score_thred_sell: 0.6
  max_sl_rate: 0.05
  max_profit_rate: 0.1
  bs_type: "1,2"

metrics:
  win_rate: 0.62
  profit_loss_ratio: 1.8
  total_return: 0.35
  max_drawdown: 0.12
  trade_count: 150
```

### 生成交易配置

```python
# parse_automl_result.py

def generate_trade_config(automl_result):
    """将AutoML结果转换为交易配置"""
    
    config = {
        'score_thred': automl_result['best_params']['score_thred'],
        'strategy_para': {
            'max_sl_rate': automl_result['best_params']['max_sl_rate'],
            'max_profit_rate': automl_result['best_params']['max_profit_rate'],
        },
        'bs_type': automl_result['best_params']['bs_type'],
    }
    
    # 保存到配置文件
    with open('Trade/Script/OpenConfig.yaml', 'w') as f:
        yaml.dump(config, f)
```

---

## 注意事项

1. **过拟合风险**: 参数过度优化可能导致过拟合
2. **样本外验证**: 必须在测试集上验证
3. **市场变化**: 历史最优不代表未来最优
4. **计算资源**: 搜索空间大时需要较多计算资源

---

## 下一步

- [交易引擎](./05-trade-engine.md) - 使用优化后的参数进行交易
- [数据库系统](./06-database.md) - 存储交易数据


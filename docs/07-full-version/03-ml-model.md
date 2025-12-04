# 机器学习模型

## 概述

完整版支持使用机器学习模型对买卖点进行评分，提高交易的准确率。

---

## 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                     机器学习模块架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    特征计算 (Features)                    │   │
│  │  ┌─────────────────────────────────────────────────┐    │   │
│  │  │  500+ 特征                                       │    │   │
│  │  │  - 笔特征: 振幅、K线数、MACD等                   │    │   │
│  │  │  - 线段特征: 笔数、中枢数等                      │    │   │
│  │  │  - 中枢特征: 区间、位置等                        │    │   │
│  │  │  - 买卖点特征: 类型、背驰度等                    │    │   │
│  │  │  - 多级别特征                                    │    │   │
│  │  └─────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    回测 (Backtest)                        │   │
│  │  - 计算历史所有买卖点的特征                              │   │
│  │  - 计算标签 (是否盈利)                                   │   │
│  │  - 输出特征文件                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 模型训练 (ModelGenerator)                  │   │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │   │
│  │  │   XGBoost   │ │  LightGBM   │ │  MLP/DNN    │        │   │
│  │  └─────────────┘ └─────────────┘ └─────────────┘        │   │
│  │                                                          │   │
│  │  - 训练集/测试集划分                                     │   │
│  │  - 模型训练                                              │   │
│  │  - 评估指标: AUC, 准确率等                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                            │                                    │
│                            ▼                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                 模型接入 (CommModel)                       │   │
│  │  - 加载模型文件                                          │   │
│  │  - 实时预测CBSP分数                                      │   │
│  │  - 根据阈值过滤                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 特征系统

### 特征分类

| 分类 | 数量 | 示例 |
|------|------|------|
| 笔特征 | ~50 | 振幅、K线数、MACD峰值 |
| 线段特征 | ~30 | 笔数、中枢数、趋势 |
| 中枢特征 | ~40 | 区间大小、位置、重叠度 |
| 买卖点特征 | ~30 | 类型、背驰度、距离 |
| 技术指标 | ~50 | RSI、KDJ、布林线位置 |
| 多级别特征 | ~100+ | 父级别/子级别特征 |
| 统计特征 | ~100+ | 均值、标准差、分位数 |

### 特征计算

```python
# ChanModel/Features.py

class CFeatures:
    def __init__(self, cbsp: CCustomBSP):
        self.cbsp = cbsp
        self.features = {}
        self._calculate()
    
    def _calculate(self):
        self._calc_bi_features()
        self._calc_seg_features()
        self._calc_zs_features()
        self._calc_bsp_features()
        # ...
    
    def _calc_bi_features(self):
        bi = self.cbsp.bsp.bi
        self.features['bi_amp'] = bi.amp()
        self.features['bi_klu_cnt'] = bi.get_klu_cnt()
        self.features['bi_macd_peak'] = bi.cal_macd_metric(MACD_ALGO.PEAK, False)
        # ...
```

### 特征访问

```python
# 获取CBSP的特征
cbsp = chan[0].cbsp_strategy[-1]
features = cbsp.features

print(features['bi_amp'])
print(features['seg_bi_cnt'])
```

---

## 模型训练框架

### CModelGenerator 基类

```python
class CModelGenerator:
    """模型生成器基类"""
    
    def train(self, train_set, test_set):
        """训练模型"""
        raise NotImplementedError
    
    def create_train_test_set(self, sample_iter):
        """创建训练/测试集"""
        raise NotImplementedError
    
    def save_model(self):
        """保存模型"""
        raise NotImplementedError
    
    def load_model(self) -> int:
        """加载模型，返回特征维度"""
        raise NotImplementedError
    
    def predict(self, dataset) -> List[float]:
        """预测"""
        raise NotImplementedError
```

### XGBoost 示例

```python
class CXGBTrainModelGenerator(CModelGenerator):
    
    def train(self, train_set, test_set):
        params = {
            'max_depth': 6,
            'eta': 0.1,
            'objective': 'binary:logistic',
            'eval_metric': 'auc',
        }
        
        self.model = xgb.train(
            params,
            train_set.data,
            num_boost_round=100,
            evals=[(test_set.data, 'test')],
        )
    
    def predict(self, dataset):
        return self.model.predict(dataset.data)
```

---

## 模型接入

### CCommModel 基类

```python
class CCommModel:
    """模型接入基类"""
    
    def __init__(self, path):
        self.load(path)
    
    def load(self, path):
        """加载模型文件"""
        raise NotImplementedError
    
    def predict(self, cbsp: CCustomBSP) -> float:
        """
        预测CBSP的分数
        
        Args:
            cbsp: 待评分的买卖点
        
        Returns:
            分数 (0-1之间，越高越好)
        """
        raise NotImplementedError
```

### 配置模型

```python
from ChanModel.XGBModel import CXGBModel

config = CChanConfig({
    "model": CXGBModel,           # 模型类
    "score_thred": 0.6,           # 分数阈值
    "cal_feature": True,          # 计算特征
})
```

---

## 回测流程

```python
# 1. 运行回测，生成特征文件
# ModelStrategy/backtest.py

def run_backtest(stock_list, config):
    for stock in stock_list:
        chan = CChan(code=stock, config=config)
        
        for cbsp in chan[0].cbsp_strategy:
            features = cbsp.features
            label = calculate_label(cbsp)
            
            save_to_file(features, label)

# 2. 训练模型
model_gen = CXGBTrainModelGenerator(...)
model_gen.trainProcess()

# 3. 评估模型
model_gen.evaluate()

# 4. 接入实盘
config = CChanConfig({
    "model": CXGBModel,
    "score_thred": 0.6,
})
```

---

## 标签定义

| 标签类型 | 说明 |
|----------|------|
| 固定收益 | 持有N天后是否盈利 |
| 动态止盈止损 | 先触达止盈还是止损 |
| 回撤收益比 | 收益/最大回撤 |

---

## 特征一致性

线上线下特征可能不一致：
- 训练时K线完整
- 实盘时K线不完整

解决方案:

```python
# ModelStrategy/FeatureReconciliation.py

def check_feature_consistency(offline_features, online_features):
    """检查特征一致性"""
    for key in offline_features:
        if abs(offline_features[key] - online_features[key]) > 0.01:
            print(f"特征 {key} 不一致")
```

---

## 下一步

- [AutoML](./04-automl.md) - 超参数自动搜索
- [交易引擎](./05-trade-engine.md) - 执行交易


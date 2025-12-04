# ChanConfig 配置详解

## 概述

`ChanConfig` 是缠论计算的核心配置类，控制笔、线段、中枢、买卖点等各个模块的行为。

---

## 基本使用

```python
from chan_config import ChanConfig

config = ChanConfig({
    "bi_strict": True,
    "seg_algo": "chan",
    "zs_combine": True,
    # ... 更多配置
})

chan = Chan(..., config=config)
```

---

## 配置分类

### 1. 笔相关配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| bi_algo | "normal" | 笔算法: normal(标准)/fx(分形即成笔) |
| bi_strict | True | 是否严格笔（至少4根合并K线） |
| bi_fx_check | "strict" | 分形检查方法 |
| gap_as_kl | False | 缺口是否算作一根K线 |
| bi_end_is_peak | True | 笔端点必须是极值 |
| bi_allow_sub_peak | True | 允许次高低点成笔 |

**bi_fx_check 选项**:
- `strict`: 严格检查（默认）
- `loss`: 宽松检查
- `half`: 部分检查
- `totally`: 完全不重叠

```python
config = ChanConfig({
    "bi_algo": "normal",
    "bi_strict": True,
    "bi_fx_check": "strict",
})
```

---

### 2. 线段相关配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| seg_algo | "chan" | 线段算法 |
| left_seg_method | "peak" | 剩余笔处理方法 |

**seg_algo 选项**:
- `chan`: 特征序列算法（默认）
- `break`: 线段破坏定义
- `1+1`: 都业华1+1终结

**left_seg_method 选项**:
- `all`: 全部收集成一段
- `peak`: 按极值分割（默认）

```python
config = ChanConfig({
    "seg_algo": "chan",
    "left_seg_method": "peak",
})
```

---

### 3. 中枢相关配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| zs_combine | True | 是否合并中枢 |
| zs_combine_mode | "zs" | 合并模式 |
| one_bi_zs | False | 是否计算单笔中枢 |
| zs_algo | "normal" | 中枢算法 |

**zs_combine_mode 选项**:
- `zs`: 中枢区间重叠才合并（默认）
- `peak`: 有K线重叠就合并

**zs_algo 选项**:
- `normal`: 段内中枢（默认）
- `over_seg`: 跨段中枢
- `auto`: 自动选择

```python
config = ChanConfig({
    "zs_combine": True,
    "zs_combine_mode": "zs",
    "zs_algo": "normal",
})
```

---

### 4. 买卖点相关配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| divergence_rate | inf | 背驰比例阈值 |
| min_zs_cnt | 1 | 一类至少经历的中枢数 |
| max_bs2_rate | 0.9999 | 二类最大回撤比例 |
| bs1_peak | True | 一类必须是极值点 |
| macd_algo | "peak" | 背驰计算算法 |
| bs_type | "1,1p,2,2s,3a,3b" | 计算哪些买卖点类型 |

**macd_algo 选项**:
- `peak`: MACD柱峰值（默认）
- `area`: MACD面积
- `full_area`: 完整MACD面积
- `slope`: 笔斜率
- `amp`: 笔涨跌幅
- `diff`: MACD差值
- `volume`: 成交量
- `amount`: 成交额

**依赖关系配置**:

| 参数 | 默认值 | 说明 |
|------|--------|------|
| bsp2_follow_1 | True | 二类必须跟在一类后 |
| bsp3_follow_1 | True | 三类必须跟在一类后 |
| bsp2s_follow_2 | False | 类二必须跟在二类后 |
| strict_bsp3 | False | 三类中枢必须紧挨一类 |
| bsp3_peak | False | 三类突破笔必须是极值 |

```python
config = ChanConfig({
    "divergence_rate": 0.9,
    "min_zs_cnt": 1,
    "max_bs2_rate": 0.618,
    "bs1_peak": True,
    "macd_algo": "peak",
    "bs_type": "1,2,3a",
})
```

---

### 5. 技术指标配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| mean_metrics | [] | 均线周期列表 |
| trend_metrics | [] | 通道线周期列表 |
| boll_n | 20 | 布林线周期 |
| cal_demark | False | 是否计算Demark |
| cal_rsi | False | 是否计算RSI |
| cal_kdj | False | 是否计算KDJ |
| rsi_cycle | 14 | RSI周期 |
| kdj_cycle | 9 | KDJ周期 |

**MACD配置**:

```python
config = ChanConfig({
    "macd": {
        "fast": 12,
        "slow": 26,
        "signal": 9,
    }
})
```

**Demark配置**:

```python
config = ChanConfig({
    "cal_demark": True,
    "demark": {
        "demark_len": 9,
        "setup_bias": 4,
        "countdown_bias": 2,
        "max_countdown": 13,
    }
})
```

---

### 6. 数据检查配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| kl_data_check | True | 是否检查K线数据 |
| max_kl_misalign_cnt | 2 | 最大K线缺失数 |
| max_kl_inconsistent_cnt | 5 | 最大时间不一致数 |
| auto_skip_illegal_sub_lv | False | 自动跳过失败级别 |
| print_warning | True | 打印警告信息 |
| print_err_time | True | 打印错误时间 |

---

### 7. 回放配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| trigger_step | True | 是否逐步回放 |
| skip_step | 0 | 跳过前N根K线 |

```python
# 动画回放
config = ChanConfig({
    "trigger_step": True,
    "skip_step": 50,
})

# 静态计算
config = ChanConfig({
    "trigger_step": False,
})
```

---

## 精确配置

可以为不同类型的买卖点单独配置：

### 后缀说明

| 后缀 | 说明 |
|------|------|
| -buy | 笔的买点 |
| -sell | 笔的卖点 |
| -seg | 线段的买卖点 |
| -segbuy | 线段的买点 |
| -segsell | 线段的卖点 |

### 示例

```python
config = ChanConfig({
    # 笔的买点: 至少2个中枢
    "min_zs_cnt-buy": 2,
    
    # 笔的卖点: 至少1个中枢
    "min_zs_cnt-sell": 1,
    
    # 线段买卖点: 使用斜率算法
    "macd_algo-seg": "slope",
    
    # 线段买点的背驰率
    "divergence_rate-segbuy": 0.8,
})
```

---

## 完整配置示例

```python
config = ChanConfig({
    # 笔配置
    "bi_algo": "normal",
    "bi_strict": True,
    "bi_fx_check": "strict",
    "gap_as_kl": False,
    "bi_end_is_peak": True,
    
    # 线段配置
    "seg_algo": "chan",
    "left_seg_method": "peak",
    
    # 中枢配置
    "zs_combine": True,
    "zs_combine_mode": "zs",
    "zs_algo": "normal",
    
    # 买卖点配置
    "divergence_rate": 0.9,
    "min_zs_cnt": 1,
    "max_bs2_rate": 0.618,
    "bs1_peak": True,
    "macd_algo": "peak",
    "bs_type": "1,1p,2,2s,3a,3b",
    
    # 技术指标
    "mean_metrics": [5, 20, 60],
    "trend_metrics": [20],
    "boll_n": 20,
    
    # 回放
    "trigger_step": False,
    
    # 数据检查
    "print_warning": True,
})
```

---

## 配置验证

配置类会自动验证参数，无效参数会抛出异常：

```python
try:
    config = ChanConfig({
        "invalid_param": True,  # 无效参数
    })
except ChanException as e:
    print(f"配置错误: {e}")
```

---

## 下一步

- [绑图配置](./02-plot-config.md) - 绑图参数详解
- [开发指南](../06-development/) - 自定义开发


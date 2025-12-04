# 常见问题 (FAQ)

## 安装问题

### Q: `cannot import name 'Self' from 'typing'`

**问题**: Python 版本过低，`Self` 类型是 Python 3.11 新增的。

**解决方案**:

方案一（推荐）：升级 Python 到 3.11+

```bash
conda create -n chan python=3.11
conda activate chan
```

方案二：安装 typing_extensions

```bash
pip install typing_extensions
```

然后修改代码中的导入:

```python
# 将
from typing import Self

# 改为
from typing_extensions import Self
```

涉及文件:
- `seg/eigen.py`
- `seg/seg.py`
- `combiner/kline_combiner.py`

---

### Q: `ModuleNotFoundError: No module named 'bi.Bi'`

**问题**: 导入路径大小写不匹配。

**解决方案**:

```python
# 将
from .Bi import Bi

# 改为
from .bi import Bi
```

检查文件名是小写还是大写，确保导入路径与文件名一致。

---

### Q: BaoStock 登录失败

**问题**: 

```python
import baostock as bs
lg = bs.login()
# error_code != '0'
```

**可能原因**:
- 非交易日
- 网络问题
- BaoStock 服务器问题

**解决方案**:
- 检查网络连接
- 确认是否是交易日
- 尝试更换网络

---

### Q: matplotlib 图表无法显示

**问题**: Windows 上运行时图表无法弹出。

**解决方案**:

```python
import matplotlib
matplotlib.use('TkAgg')  # 或 'Qt5Agg'

# 然后再导入 pyplot
import matplotlib.pyplot as plt
```

---

## 使用问题

### Q: 如何查看某只股票的缠论分析？

```python
from chan import Chan
from chan_config import ChanConfig
from common.enums import DATA_SRC, KL_TYPE

config = ChanConfig({"trigger_step": False})

chan = Chan(
    code="sz.000001",
    begin_time="2023-01-01",
    end_time="2023-12-31",
    data_src=DATA_SRC.BAO_STOCK,
    lv_list=[KL_TYPE.K_DAY],
    config=config,
)

# 查看笔
for bi in chan[0].bi_list:
    print(bi)

# 查看线段
for seg in chan[0].seg_list:
    print(seg)
```

---

### Q: 如何保存绑图结果？

```python
from plot.plot_driver import PlotDriver

driver = PlotDriver(chan, plot_config={"plot_bi": True})

# 保存为图片
driver.save2img("result.png")

# 保存为PDF
driver.save2img("result.pdf")
```

---

### Q: 如何只显示最近N根K线？

```python
plot_para = {
    "figure": {
        "x_range": 200,  # 最后200根K线
    }
}

# 或者按笔/段
plot_para = {
    "figure": {
        "x_bi_cnt": 20,   # 最后20笔
        "x_seg_cnt": 5,   # 最后5段
    }
}
```

---

### Q: 如何获取买卖点？

```python
# 获取所有买卖点
for bsp in chan[0].bs_point_lst:
    print(f"类型: {bsp.type}, 买/卖: {'买' if bsp.is_buy else '卖'}")

# 获取最近N个买卖点
latest = chan.get_latest_bsp(number=5)
```

---

### Q: 如何进行多级别分析？

```python
chan = Chan(
    code="sz.000001",
    lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_60M],  # 从大到小
    ...
)

# 访问日线
day_data = chan[KL_TYPE.K_DAY]  # 或 chan[0]

# 访问60分钟
m60_data = chan[KL_TYPE.K_60M]  # 或 chan[1]
```

---

## 配置问题

### Q: 如何调整笔的严格程度？

```python
config = ChanConfig({
    "bi_strict": False,      # 非严格笔
    "bi_fx_check": "loss",   # 宽松的分形检查
})
```

---

### Q: 如何调整买卖点的判断条件？

```python
config = ChanConfig({
    "divergence_rate": 0.8,   # 背驰比例
    "min_zs_cnt": 2,          # 至少2个中枢
    "max_bs2_rate": 0.618,    # 二类最大回撤
    "bs_type": "1,2,3a",      # 只计算这些类型
})
```

---

### Q: 如何配置技术指标？

```python
config = ChanConfig({
    "mean_metrics": [5, 20, 60],  # 均线
    "trend_metrics": [20],        # 通道线
    "boll_n": 20,                 # 布林线
    "cal_rsi": True,              # RSI
    "cal_kdj": True,              # KDJ
})
```

---

## 数据问题

### Q: 如何使用自己的数据？

使用 CSV 数据源:

```python
chan = Chan(
    code="./data/my_stock.csv",
    data_src=DATA_SRC.CSV,
    ...
)
```

CSV 格式:

```csv
time_key,open,high,low,close,volume
2023-01-03,10.00,10.50,9.80,10.20,1000000
```

---

### Q: K线时间错误怎么办？

**错误**: `KL_NOT_MONOTONOUS` - K线时间不单调

**原因**: K线时间不是严格递增的

**解决方案**:
- 检查数据源的时间格式
- 确保时间按升序排列
- 检查是否有重复时间

---

### Q: 次级别找不到K线怎么办？

**错误**: `KL_DATA_NOT_ALIGN`

**原因**: 父级别和子级别的K线数据不对齐

**解决方案**:

```python
config = ChanConfig({
    "max_kl_misalign_cnt": 5,   # 增加容忍度
    "auto_skip_illegal_sub_lv": True,  # 自动跳过失败的级别
})
```

---

## 性能问题

### Q: 计算很慢怎么办？

1. 减少K线数量:

```python
chan = Chan(
    begin_time="2023-01-01",  # 缩短时间范围
    ...
)
```

2. 只计算单级别:

```python
chan = Chan(
    lv_list=[KL_TYPE.K_DAY],  # 只用日线
    ...
)
```

3. 使用 Python 3.11（性能提升约16%）

---

### Q: 批量计算多只股票时很慢？

使用 `only_judge_last` 配置:

```python
config = ChanConfig({
    "only_judge_last": True,  # 只计算最后一根K线的买卖点
})
```

---

## 其他问题

### Q: 项目最低 Python 版本是多少？

- 公开版: Python 3.8+（需要处理 `Self` 类型兼容性）
- 推荐: Python 3.11+（性能最佳）

---

### Q: 如何获取完整版？

完整版暂未开源，如有需求可以：
- 联系作者
- 参考 README 中的联系方式

---

### Q: 文档/代码有问题怎么反馈？

- GitHub Issues
- Telegram 讨论组

---

## 下一步

- [API速查](../09-appendix/api-reference.md) - 接口参考
- [术语表](../09-appendix/glossary.md) - 专业术语


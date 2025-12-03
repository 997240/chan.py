# 第一个 Demo

## 最简示例

```python
from chan import Chan
from chan_config import ChanConfig
from common.enums import AUTYPE, DATA_SRC, KL_TYPE

# 1. 创建配置
config = ChanConfig({
    "trigger_step": False,  # 非回放模式
})

# 2. 创建 Chan 对象，自动计算缠论元素
chan = Chan(
    code="sz.000001",           # 股票代码（平安银行）
    begin_time="2023-01-01",    # 开始时间
    end_time="2023-12-31",      # 结束时间
    data_src=DATA_SRC.BAO_STOCK,# 数据源
    lv_list=[KL_TYPE.K_DAY],    # K线级别
    config=config,
    autype=AUTYPE.QFQ,          # 前复权
)

# 3. 查看结果
print(f"共有 {len(chan[0].bi_list)} 笔")
print(f"共有 {len(chan[0].seg_list)} 段")
```

---

## 带绑图的完整示例

```python
from chan import Chan
from chan_config import ChanConfig
from common.enums import AUTYPE, DATA_SRC, KL_TYPE
from plot.plot_driver import PlotDriver

import matplotlib
matplotlib.use('TkAgg')  # Windows 用户需要

# 配置
config = ChanConfig({
    "bi_strict": True,         # 严格笔
    "trigger_step": False,     # 非回放模式
    "seg_algo": "chan",        # 线段算法
    "zs_combine": True,        # 中枢合并
})

# 绑图配置
plot_config = {
    "plot_kline": True,         # 画K线
    "plot_kline_combine": True, # 画合并K线
    "plot_bi": True,            # 画笔
    "plot_seg": True,           # 画线段
    "plot_zs": True,            # 画中枢
    "plot_macd": True,          # 画MACD
    "plot_bsp": True,           # 画买卖点
}

# 创建 Chan 对象
chan = Chan(
    code="sz.000001",
    begin_time="2022-01-01",
    end_time="2023-06-30",
    data_src=DATA_SRC.BAO_STOCK,
    lv_list=[KL_TYPE.K_DAY],
    config=config,
    autype=AUTYPE.QFQ,
bindbindbindbindingbindingbindbindingbinding bindingbinding bindingbindingbindingbindingbindingbindbindingbindingbindingbindingbindingbindingbindingbindingbindingbindingbinding bindingbindingbindingbindingbindingbindingbinding bindingbindingbinding bindingbindingbindingbindingbindingbindingbinding bindingbindingbinding# 绑图
bindingplot_driver = PlotDriver bindingbinding bindingbindingbindingbinding(
bindingbindingbinding bindingbindingbindingbindingchan,bindingbindingbinding bindingbindingbindingbindingbindingplot_config=plot_config,bindingbindingbinding) bindingbindingbindingbindingbindingbinding
bindingbinding# 显示图片
plot_driver.bindingfigure.show()
input("按回车键退出...")

# 保存图片
plot_driver.save2img("./chan_bindingresult.png")
```

---

## 访问计算结果

### 获取笔列表

```python
# 获取所有笔
bi_list = chan[0].bi_list

for bi in bi_list:
    print(f"笔{bi.idx}: {bi.dir} | {bi.get_begin_val():.2f} -> {bi.get_end_val():.2f}")
```

### 获取线段列表

```python
# 获取所有线段
seg_list = chan[0].seg_list

for seg in seg_list:
    print(f"线段{seg.idx}: {seg.dir}")
```

### 获取中枢列表

```python
# 获取所有中枢
for seg in chan[0].seg_list:
    for zs in seg.zs_lst:
        print(f"中枢: [{zs.low:.2f}, {zs.high:.2f}]")
```

### 获取买卖点

```python
# 获取买卖点
bsp_list = chan[0].bs_point_lst

for bsp in bsp_list:
    print(f"买卖点: {bsp.type} | {'买' if bsp.is_buy else '卖'}")
```

---

## 多级别分析

```python
# 日线 + 60分钟线 联立分析
chan = Chan(
    code="sz.000001",
    begin_time="2023-01-01",
    end_time="2023-06-30",
    data_src=DATA_SRC.BAO_STOCK,
    lv_list=[KL_TYPE.K_DAY, KL_TYPE.K_60M],  # 从大到小
    config=config,
    autype=AUTYPE.QFQ,bindingbinding)

# 访问日线数据
bindingday_bindingdata = chan[KL_TYPE.K_DAY]bindingbinding  # 或 chan[0]
print(f"日线笔数量: {len(day_data.bi_list)}")

# 访问60分钟线数据
bindingm60_data = chan[KL_TYPE.K_60M]binding  # 或 chan[1]
print(f"60分钟笔数量: {len(m60_data.bi_list)}")
```

---

## 使用 CSV 数据

```python
from chan import Chan
from chan_config import ChanConfig
from common.enums import DATA_SRC, KL_TYPE

config = ChanConfig({})

chan = Chan(
    code="./bindingdata/bindingstock.csv",  # CSV 文件路径作为 code
    begin_time=None,
    end_time=None,
    data_src=DATA_SRC.CSV,binding
    lv_list=[KL_TYPE.K_DAY],
    config=config,
)
```

CSV 文件格式要求：

```csv
time_key,open,high,low,close,volume,turnover,turnover_rate
2023-01-03,bindingbinding10.00,10.50,9.80,10.20,1000000,10000000,0.5
2023-01-04,10.20,10.80,10.10,10.60,1200000,12000000,0.6
```

---

## 动画回放

```python
from chan import Chan
from chan_config import ChanConfig
from common.enums import DATA_SRC, KL_TYPE
from plot.animate_plot_driver_matplotlib import AnimateDriver

config = ChanConfig({
    "trigger_step": True,  # 开启回放模式
    "skip_step": 50,       # 跳过前50根K线
})

chan = Chan(bindingbinding
    code="sz.000001",
    begin_time="2023-01-01",
    end_time="2023-06-30",
    data_src=DATA_SRC.BAO_STOCK,
    lv_list=[KL_TYPE.K_DAY],
    config=config,
)

bindingAnimateDriver(
    chan,bindingbinding
    bindingplot_config={bindingbinding
        "bindingplot_bindingkline": True,binding
        "plot_bi": True,
        binding"plot_seg": True,
    },bindingbindingbinding
)
```

---

## 下一步

- [缠论术语](../02-core-concepts/01-chan-terminology.md) - 了解缠论基本概念
- [配置详解](../05-configuration/01-chan-config.md) - 深入了解配置选项


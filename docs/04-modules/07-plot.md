# 绑图模块 (plot)

## 模块概述

`plot/` 模块负责缠论分析结果的可视化，支持静态图和动画回放。

---

## 目录结构

```
plot/
├── __init__.py
├── plot_driver.py                    # 静态图驱动
├── plot_meta.py                      # 图元数据
├── animate_plot_driver_matplotlib.py # 动画驱动
└── animate_plot_driver_jupyter.py    # Jupyter动画
```

---

## 快速使用

### 静态图

```python
from plot.plot_driver import PlotDriver

chan = Chan(...)

# 绑图配置
plot_config = {
    "plot_kline": True,
    "plot_bi": True,
    "plot_seg": True,
    "plot_zs": True,
}

# 创建绑图
driver = PlotDriver(chan, plot_config=plot_config)

# 显示
driver.figure.show()

# 保存
driver.save2img("result.png")
```

### 动画回放

```python
from plot.animate_plot_driver_matplotlib import AnimateDriver

config = ChanConfig({
    "trigger_step": True,  # 必须开启
    "skip_step": 50,       # 跳过前50根K线
})

chan = Chan(..., config=config)

AnimateDriver(chan, plot_config=plot_config)
```

---

## plot_config 配置

控制绘制哪些元素：

| 配置项 | 默认 | 说明 |
|--------|------|------|
| plot_kline | False | 绘制K线 |
| plot_kline_combine | False | 绘制合并K线 |
| plot_bi | False | 绘制笔 |
| plot_seg | False | 绘制线段 |
| plot_eigen | False | 绘制特征序列 |
| plot_zs | False | 绘制中枢 |
| plot_bsp | False | 绘制买卖点 |
| plot_macd | False | 绘制MACD |
| plot_mean | False | 绘制均线 |
| plot_boll | False | 绘制布林线 |
| plot_channel | False | 绘制通道线 |
| plot_demark | False | 绘制Demark指标 |
| plot_rsi | False | 绘制RSI |
| plot_kdj | False | 绘制KDJ |

### 配置格式

```python
# 字典格式
plot_config = {"plot_bi": True, "plot_seg": True}

# 列表格式
plot_config = ["plot_bi", "plot_seg"]

# 字符串格式
plot_config = "plot_bi,plot_seg"

# 可省略 "plot_" 前缀
plot_config = ["bi", "seg"]
```

---

## plot_para 配置

控制绘图细节：

### figure (图表)

```python
plot_para = {
    "figure": {
        "w": 20,              # 宽度
        "h": 10,              # 高度
        "macd_h": 0.3,        # MACD高度比例
        "x_range": 200,       # 只显示最后N根K线
        "x_bi_cnt": 0,        # 只显示最后N笔
        "x_seg_cnt": 0,       # 只显示最后N段
        "grid": "xy",         # 网格: x/y/xy/None
    }
}
```

### kl (K线)

```python
plot_para = {
    "kl": {
        "width": 0.4,         # K线宽度
        "rugd": True,         # 红涨绿跌
        "plot_mode": "kl",    # kl/close/open/high/low
    }
}
```

### bi (笔)

```python
plot_para = {
    "bi": {
        "color": "black",     # 颜色
        "show_num": False,    # 显示序号
        "disp_end": False,    # 显示端点价格
    }
}
```

### seg (线段)

```python
plot_para = {
    "seg": {
        "width": 5,           # 线宽
        "color": "g",         # 颜色
        "plot_trendline": True,  # 绘制趋势线
        "show_num": False,    # 显示序号
    }
}
```

### zs (中枢)

```python
plot_para = {
    "zs": {
        "color": "orange",    # 颜色
        "linewidth": 2,       # 线宽
        "show_text": False,   # 显示高低点数值
    }
}
```

### bsp (买卖点)

```python
plot_para = {
    "bsp": {
        "buy_color": "r",     # 买点颜色
        "sell_color": "g",    # 卖点颜色
        "fontsize": 15,       # 字体大小
        "arrow_l": 0.15,      # 箭头长度
    }
}
```

### macd

```python
plot_para = {
    "macd": {
        "width": 0.4,         # 柱子宽度
    }
}
```

---

## 完整示例

```python
from chan import Chan
from chan_config import ChanConfig
from common.enums import DATA_SRC, KL_TYPE
from plot.plot_driver import PlotDriver

import matplotlib
matplotlib.use('TkAgg')

config = ChanConfig({
    "bi_strict": True,
    "trigger_step": False,
})

plot_config = {
    "plot_kline": True,
    "plot_kline_combine": True,
    "plot_bi": True,
    "plot_seg": True,
    "plot_zs": True,
    "plot_bsp": True,
    "plot_macd": True,
}

plot_para = {
    "figure": {
        "w": 24,
        "h": 12,
    },
    "bi": {
        "show_num": True,
        "disp_end": True,
    },
    "seg": {
        "plot_trendline": True,
    },
    "zs": {
        "show_text": True,
    },
}

chan = Chan(
    code="sz.000001",
    begin_time="2023-01-01",
    end_time="2023-12-31",
    data_src=DATA_SRC.BAO_STOCK,
    lv_list=[KL_TYPE.K_DAY],
    config=config,
)

driver = PlotDriver(
    chan,
    plot_config=plot_config,
    plot_para=plot_para,
)

driver.figure.show()
driver.save2img("./chan_analysis.png")
```

---

## 多级别绘图

```python
# 只绘制最高级别
plot_para = {
    "figure": {
        "only_top_lv": True,
    }
}

# 或分级别配置
plot_config = {
    KL_TYPE.K_DAY: ["bi", "seg", "zs"],
    KL_TYPE.K_60M: ["bi"],
}
```

---

## 自定义标记

```python
plot_para = {
    "marker": {
        "markers": {
            "2023/06/01": ("买入信号", "up", "red"),
            "2023/08/15": ("卖出信号", "down", "green"),
        }
    }
}
```

---

## 常见问题

### matplotlib 后端问题

```python
import matplotlib
matplotlib.use('TkAgg')  # Windows
# 或
matplotlib.use('Qt5Agg')
```

### 图片显示不完整

```python
plot_para = {
    "figure": {
        "w": 30,  # 增加宽度
        "h": 15,  # 增加高度
    }
}
```

---

## 下一步

- [绑图配置详解](../05-configuration/02-plot-config.md) - 更多配置选项
- [数学工具](./08-math-util.md) - 技术指标


# 绑图配置详解

## 概述

绑图配置分为两部分：
- `plot_config`: 控制绘制哪些元素
- `plot_para`: 控制绘制细节

---

## plot_config

### 基本用法

```python
plot_config = {
    "plot_kline": True,
    "plot_bi": True,
    "plot_seg": True,
}
```

### 支持的格式

```python
# 字典格式
plot_config = {"plot_bi": True, "plot_seg": True}

# 列表格式
plot_config = ["plot_bi", "plot_seg"]

# 字符串格式
plot_config = "plot_bi,plot_seg"

# 省略 "plot_" 前缀
plot_config = ["bi", "seg"]
```

### 完整选项

| 选项 | 说明 |
|------|------|
| plot_kline | K线 |
| plot_kline_combine | 合并K线 |
| plot_bi | 笔 |
| plot_seg | 线段 |
| plot_eigen | 特征序列 |
| plot_zs | 中枢 |
| plot_bsp | 买卖点 |
| plot_segseg | 线段的线段 |
| plot_segzs | 线段中枢 |
| plot_segbsp | 线段买卖点 |
| plot_macd | MACD图 |
| plot_mean | 均线 |
| plot_boll | 布林线 |
| plot_channel | 通道线 |
| plot_demark | Demark指标 |
| plot_rsi | RSI指标 |
| plot_kdj | KDJ指标 |
| plot_marker | 自定义标记 |

### 多级别配置

```python
from common.enums import KL_TYPE

plot_config = {
    KL_TYPE.K_DAY: ["bi", "seg", "zs", "bsp"],
    KL_TYPE.K_60M: ["bi", "seg"],
}
```

---

## plot_para

### figure (图表设置)

```python
plot_para = {
    "figure": {
        "w": 20,              # 图表宽度
        "h": 10,              # 图表高度
        "macd_h": 0.3,        # MACD高度占比
        "only_top_lv": False, # 只绘制最高级别
        "x_range": 0,         # 显示最后N根K线 (0=全部)
        "x_bi_cnt": 0,        # 显示最后N笔 (0=全部)
        "x_seg_cnt": 0,       # 显示最后N段 (0=全部)
        "x_begin_date": "0",  # 开始日期 (YYYY/MM/DD)
        "x_end_date": "0",    # 结束日期 (YYYY/MM/DD)
        "x_tick_num": 10,     # X轴刻度数
        "grid": "xy",         # 网格: x/y/xy/None
    }
}
```

### kl (K线设置)

```python
plot_para = {
    "kl": {
        "width": 0.4,         # K线宽度
        "rugd": True,         # 红涨绿跌
        "plot_mode": "kl",    # 绘制模式: kl/close/open/high/low
    }
}
```

### klc (合并K线设置)

```python
plot_para = {
    "klc": {
        "width": 0.4,             # 宽度
        "plot_single_kl": True,   # 单根K线是否画框
    }
}
```

### bi (笔设置)

```python
plot_para = {
    "bi": {
        "color": "black",         # 颜色
        "show_num": False,        # 显示序号
        "num_color": "red",       # 序号颜色
        "num_fontsize": 15,       # 序号字体
        "disp_end": False,        # 显示端点价格
        "end_color": "black",     # 价格颜色
        "end_fontsize": 10,       # 价格字体
        "sub_lv_cnt": None,       # 次级别显示笔数
        "facecolor": "green",     # 次级别范围颜色
        "alpha": 0.1,             # 透明度
    }
}
```

### seg (线段设置)

```python
plot_para = {
    "seg": {
        "width": 5,               # 线宽
        "color": "g",             # 颜色
        "show_num": False,        # 显示序号
        "num_color": "blue",      # 序号颜色
        "num_fontsize": 30,       # 序号字体
        "disp_end": False,        # 显示端点价格
        "end_color": "g",         # 价格颜色
        "end_fontsize": 13,       # 价格字体
        "plot_trendline": False,  # 绘制趋势线
        "trendline_color": "r",   # 趋势线颜色
        "trendline_width": 3,     # 趋势线宽度
    }
}
```

### zs (中枢设置)

```python
plot_para = {
    "zs": {
        "color": "orange",        # 颜色
        "linewidth": 2,           # 线宽
        "sub_linewidth": 0.5,     # 子中枢线宽
        "show_text": False,       # 显示高低点数值
        "fontsize": 14,           # 字体大小
        "text_color": "orange",   # 文字颜色
        "draw_one_bi_zs": False,  # 绘制单笔中枢
    }
}
```

### bsp (买卖点设置)

```python
plot_para = {
    "bsp": {
        "buy_color": "r",         # 买点颜色
        "sell_color": "g",        # 卖点颜色
        "fontsize": 15,           # 字体大小
        "arrow_l": 0.15,          # 箭头长度
        "arrow_h": 0.2,           # 箭头头部
        "arrow_w": 1,             # 箭头宽度
    }
}
```

### eigen (特征序列设置)

```python
plot_para = {
    "eigen": {
        "color_top": "r",         # 顶分型颜色
        "color_bottom": "b",      # 底分型颜色
        "alpha": 0.5,             # 透明度
        "only_peak": False,       # 只画顶底分型
    }
}
```

### macd (MACD设置)

```python
plot_para = {
    "macd": {
        "width": 0.4,             # 柱子宽度
    }
}
```

### boll (布林线设置)

```python
plot_para = {
    "boll": {
        "mid_color": "black",     # 中轨颜色
        "up_color": "blue",       # 上轨颜色
        "down_color": "purple",   # 下轨颜色
    }
}
```

### channel (通道线设置)

```python
plot_para = {
    "channel": {
        "T": None,                # 周期 (None=最大)
        "top_color": "r",         # 上轨颜色
        "bottom_color": "b",      # 下轨颜色
        "linewidth": 3,           # 线宽
        "linestyle": "solid",     # 线型
    }
}
```

### marker (自定义标记)

```python
plot_para = {
    "marker": {
        "markers": {
            "2023/06/01": ("买入", "up", "red"),
            "2023/08/15": ("卖出", "down", "green"),
            "2023/10/01": ("观望", "up"),  # 使用默认颜色
        },
        "arrow_l": 0.15,
        "arrow_h": 0.2,
        "arrow_w": 1,
        "fontsize": 14,
        "default_color": "b",
    }
}
```

### demark (Demark设置)

```python
plot_para = {
    "demark": {
        "setup_color": "b",           # setup颜色
        "countdown_color": "r",       # countdown颜色
        "fontsize": 12,               # 字体
        "min_setup": 9,               # 最小setup显示
        "max_countdown_background": "yellow",
        "begin_line_color": "purple",
        "begin_line_style": "dashed",
    }
}
```

### rsi (RSI设置)

```python
plot_para = {
    "rsi": {
        "color": "b",
    }
}
```

### kdj (KDJ设置)

```python
plot_para = {
    "kdj": {
        "k_color": "orange",
        "d_color": "blue",
        "j_color": "pink",
    }
}
```

---

## 完整示例

```python
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
        "grid": "xy",
    },
    "bi": {
        "show_num": True,
        "disp_end": True,
    },
    "seg": {
        "plot_trendline": True,
        "show_num": True,
    },
    "zs": {
        "show_text": True,
    },
    "marker": {
        "markers": {
            "2023/06/01": ("关注", "up", "blue"),
        }
    }
}

driver = PlotDriver(
    chan,
    plot_config=plot_config,
    plot_para=plot_para,
)
```

---

## 下一步

- [开发指南](../06-development/) - 自定义开发
- [FAQ](../08-faq/faq.md) - 常见问题


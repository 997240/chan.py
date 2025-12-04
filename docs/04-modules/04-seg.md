# 线段模块 (seg)

## 模块概述

`seg/` 模块负责线段的计算和管理，线段是对笔的更高级别抽象。

---

## 目录结构

```
seg/
├── __init__.py
├── seg.py              # 线段类
├── seg_config.py       # 线段配置
├── seg_list_comm.py    # 线段列表基类
├── seg_list_chan.py    # 特征序列算法
├── seg_list_def.py     # 定义算法
├── seg_list_dyh.py     # 1+1终结算法
├── eigen.py            # 特征序列
└── eigen_fx.py         # 特征序列分形
```

---

## 核心概念

### 什么是线段？

线段由至少3笔构成：
- 第一笔决定线段方向
- 线段有确定和不确定状态

```
上升线段（5笔）:

           ●
          /|\
         / | \
        /  |  \
       ●   |   ●
      /|   |   |\
     / |   |   | \
    ●  |   |   |  ●
   笔1 笔2 笔3 笔4 笔5
```

### 线段算法

项目支持三种线段计算算法：

| 算法 | 配置值 | 说明 |
|------|--------|------|
| 特征序列 | "chan" | 基于特征序列分形（默认） |
| 定义法 | "break" | 基于线段破坏定义 |
| 1+1终结 | "1+1" | 都业华版本 |

---

## Seg 类

### 主要属性

```python
class Seg:
    idx: int              # 线段序号
    dir: BI_DIR           # 方向
    start_bi: Bi          # 起始笔
    end_bi: Bi            # 结束笔
    is_sure: bool         # 是否确定
    
    zs_lst: List[ZS]      # 中枢列表
    
    pre: Seg              # 前一线段
    next: Seg             # 后一线段
```

### 主要方法

```python
# 方向判断
seg.is_up()              # 是否上升
seg.is_down()            # 是否下降

# 价格获取
seg.get_begin_val()      # 起点价格
seg.get_end_val()        # 终点价格

# 属性计算
seg.cal_bi_cnt()         # 包含的笔数量
seg.amp()                # 振幅
```

---

## 特征序列 (Eigen)

特征序列用于确定线段的结束。

### 概念

将同向的笔组成特征序列元素：
- 上升线段: 取向下的笔组成特征序列
- 下降线段: 取向上的笔组成特征序列

```
上升线段的特征序列:

原始:    ●     ●
        /|\   /|\
       / | \ / | \
      ●  |  ●  |  ●
         |     |
    特征序列元素1 特征序列元素2
```

### 特征序列分形

当特征序列出现顶/底分形时，线段可能结束。

---

## SegList 使用

### 访问线段

```python
chan = Chan(...)

# 遍历线段
for seg in chan[0].seg_list:
    direction = "↑" if seg.is_up() else "↓"
    print(f"线段{seg.idx} {direction}")
    print(f"  起点: {seg.get_begin_val():.2f}")
    print(f"  终点: {seg.get_end_val():.2f}")
    print(f"  笔数: {seg.cal_bi_cnt()}")
    print(f"  中枢数: {len(seg.zs_lst)}")
```

### 获取线段内的笔

```python
seg = chan[0].seg_list[-1]

# 遍历线段内的笔
bi = seg.start_bi
while bi and bi.idx <= seg.end_bi.idx:
    print(f"  笔{bi.idx}: {bi.dir}")
    bi = bi.next
```

---

## 配置参数

### SegConfig

```python
config = ChanConfig({
    "seg_algo": "chan",           # 线段算法
    "left_seg_method": "peak",    # 剩余笔处理方法
})
```

### seg_algo 选项

| 值 | 说明 |
|------|------|
| "chan" | 特征序列算法（默认） |
| "break" | 线段破坏定义 |
| "1+1" | 都业华1+1终结 |

### left_seg_method 选项

处理不能归入确定线段的笔：

| 值 | 说明 |
|------|------|
| "all" | 全部收集成一段 |
| "peak" | 按极值点分割（默认） |

---

## 线段的线段 (segseg)

可以把线段当作笔，计算更高级别的结构：

```python
# 访问线段的线段
for segseg in chan[0].segseg_list:
    print(f"线段的线段: {segseg.idx}")
```

这对应于父级别的走势分析。

---

## 使用示例

### 统计线段信息

```python
chan = Chan(...)

seg_list = chan[0].seg_list

# 统计
total = len(seg_list)
up_count = sum(1 for s in seg_list if s.is_up())
down_count = total - up_count

print(f"总线段数: {total}")
print(f"上升线段: {up_count}")
print(f"下降线段: {down_count}")

# 平均笔数
avg_bi = sum(s.cal_bi_cnt() for s in seg_list) / total
print(f"平均笔数: {avg_bi:.1f}")
```

### 查找包含多个中枢的线段

```python
for seg in chan[0].seg_list:
    if len(seg.zs_lst) >= 2:
        print(f"线段{seg.idx} 包含 {len(seg.zs_lst)} 个中枢")
        for zs in seg.zs_lst:
            print(f"  中枢: [{zs.low:.2f}, {zs.high:.2f}]")
```

### 分析线段趋势

```python
# 判断当前趋势
last_seg = chan[0].seg_list[-1]
prev_seg = last_seg.pre

if last_seg.is_up():
    if prev_seg and prev_seg.is_down():
        if last_seg.get_end_val() > prev_seg.get_begin_val():
            print("可能进入上升趋势")
        else:
            print("仍在下降趋势的反弹中")
```

---

## 算法选择建议

| 场景 | 推荐算法 |
|------|----------|
| 标准缠论分析 | chan |
| 追求更多细节 | break |
| 都业华体系 | 1+1 |

---

## 下一步

- [中枢模块](./05-zs.md) - 了解中枢计算
- [自定义线段算法](../06-development/03-custom-seg-algo.md) - 开发自定义算法


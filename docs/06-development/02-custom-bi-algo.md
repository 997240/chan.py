# 自定义笔算法

## 概述

本文档介绍如何修改或扩展笔的计算逻辑。

---

## 笔计算流程

```
合并K线 (KLine)
    │
    ▼
分形识别 (FX_TYPE)
    │
    ▼
成笔判断 (BiList.can_make_bi)
    │
    ▼
笔列表 (BiList)
```

---

## 核心类: BiList

笔的计算主要在 `bi/bi_list.py` 中。

### 关键方法

```python
class BiList:
    def update_bi(self, klc, last_klc, cal_virtual):
        """每根新K线时调用，更新笔"""
        pass
    
    def can_make_bi(self, klc, last_end, for_virtual=False):
        """判断是否可以成笔"""
        pass
    
    def satisfy_bi_span(self, klc, last_end):
        """检查跨越条件"""
        pass
    
    def add_new_bi(self, pre_klc, cur_klc, is_sure=True):
        """添加新笔"""
        pass
```

---

## 修改笔算法

### 方式一: 通过配置

```python
config = ChanConfig({
    # 笔算法
    "bi_algo": "normal",      # normal 或 fx
    
    # 严格笔
    "bi_strict": True,        # True: 至少4根KLC
    
    # 分形检查
    "bi_fx_check": "strict",  # strict/loss/half/totally
    
    # 缺口处理
    "gap_as_kl": False,       # True: 缺口算一根K线
    
    # 端点极值
    "bi_end_is_peak": True,   # True: 端点必须是极值
    
    # 次高低点
    "bi_allow_sub_peak": True, # True: 允许次高低点成笔
})
```

### 方式二: 修改判断逻辑

修改 `can_make_bi` 方法：

```python
# bi/bi_list.py

def can_make_bi(self, klc: KLine, last_end: KLine, for_virtual: bool = False):
    # 1. 检查跨越条件
    satisify_span = True if self.config.bi_algo == 'fx' else self.satisfy_bi_span(klc, last_end)
    if not satisify_span:
        return False
    
    # 2. 检查分形有效性
    if not last_end.check_fx_valid(klc, self.config.bi_fx_check, for_virtual):
        return False
    
    # 3. 检查端点极值（可在此添加自定义逻辑）
    if self.config.bi_end_is_peak and not end_is_peak(last_end, klc):
        return False
    
    # 4. 添加你的自定义条件
    # if not self.custom_condition(klc, last_end):
    #     return False
    
    return True
```

### 方式三: 继承 BiList

```python
# my_bi_list.py

from bi.bi_list import BiList

class MyBiList(BiList):
    """自定义笔列表"""
    
    def can_make_bi(self, klc, last_end, for_virtual=False):
        # 先调用父类方法
        if not super().can_make_bi(klc, last_end, for_virtual):
            return False
        
        # 添加自定义条件
        # 例如: 要求笔的振幅超过某个阈值
        if self._calc_amplitude(klc, last_end) < 0.02:  # 2%
            return False
        
        return True
    
    def _calc_amplitude(self, klc, last_end):
        """计算振幅"""
        if last_end.fx == FX_TYPE.BOTTOM:
            return (klc.high - last_end.low) / last_end.low
        else:
            return (last_end.high - klc.low) / last_end.high
```

---

## 配置参数详解

### bi_strict (严格笔)

```python
# 严格笔: 顶底分形之间至少4根合并K线
"bi_strict": True

# 非严格笔: 至少3根合并K线 且 至少3根原始K线
"bi_strict": False
```

### bi_fx_check (分形检查)

```python
# strict: 底分形最低点 < 顶分形三元素的最小低点
"bi_fx_check": "strict"

# loss: 底分形最低点 < 顶分形中间元素低点
"bi_fx_check": "loss"

# half: 底分形最低点 < 顶分形前两元素的最小低点
"bi_fx_check": "half"

# totally: 底分形最高点 < 顶分形最低点（完全不重叠）
"bi_fx_check": "totally"
```

### bi_algo (笔算法)

```python
# normal: 标准笔算法，需要满足各种条件
"bi_algo": "normal"

# fx: 顶底分形即成笔，无需其他条件
"bi_algo": "fx"
```

---

## 添加新的笔类型

如果需要标记不同类型的笔：

```python
# common/enums.py 添加新类型
class BI_TYPE(Enum):
    UNKNOWN = auto()
    STRICT = auto()
    SUB_VALUE = auto()
    CUSTOM = auto()  # 新类型

# bi/bi.py 设置类型
class Bi:
    def __init__(self, ...):
        self.__type = BI_TYPE.STRICT
    
    def set_type(self, bi_type):
        self.__type = bi_type
```

---

## 调试技巧

### 打印笔信息

```python
for bi in chan[0].bi_list:
    print(f"笔{bi.idx}: {bi.dir}")
    print(f"  起点: KLC{bi.begin_klc.idx} = {bi.get_begin_val():.2f}")
    print(f"  终点: KLC{bi.end_klc.idx} = {bi.get_end_val():.2f}")
    print(f"  确定: {bi.is_sure}")
    print(f"  类型: {bi.type}")
```

### 检查分形

```python
for klc in chan[0]:
    if klc.fx != FX_TYPE.UNKNOWN:
        print(f"KLC{klc.idx}: {klc.fx}, high={klc.high:.2f}, low={klc.low:.2f}")
```

---

## 注意事项

1. **保持双向链表**: 修改笔后确保 `pre` 和 `next` 正确
2. **清除缓存**: 修改笔属性后调用 `bi.clean_cache()`
3. **虚笔处理**: 注意处理最后一笔可能是虚笔的情况
4. **测试验证**: 修改后用多只股票测试，确保不会出错

---

## 下一步

- [自定义线段算法](./03-custom-seg-algo.md) - 开发线段算法
- [代码规范](./04-code-style.md) - 编码约定


# 自定义线段算法

## 概述

本文档介绍如何开发自定义的线段计算算法。

---

## 现有算法

| 算法 | 类名 | 说明 |
|------|------|------|
| chan | SegListChan | 特征序列算法（默认） |
| break | SegListDef | 线段破坏定义 |
| 1+1 | SegListDYH | 都业华1+1终结 |

---

## 算法基类: SegListComm

所有线段算法都继承自 `seg/seg_list_comm.py`。

### 核心方法

```python
class SegListComm:
    def __init__(self, seg_config, lv):
        self.lst = []           # 线段列表
        self.config = seg_config
        self.lv = lv
    
    def update(self, bi: Bi):
        """
        每添加一笔时调用
        子类必须实现
        """
        raise NotImplementedError
    
    def add_new_seg(self, ...):
        """添加新线段"""
        pass
    
    def collect_left_seg(self, ...):
        """处理剩余的笔"""
        pass
```

---

## 开发步骤

### 1. 创建新的线段算法类

```python
# seg/seg_list_custom.py

from typing import List, Optional
from bi.bi import Bi
from common.enums import BI_DIR
from seg.seg import Seg
from seg.seg_list_comm import SegListComm


class SegListCustom(SegListComm):
    """自定义线段算法"""
    
    def __init__(self, seg_config, lv):
        super().__init__(seg_config, lv)
        # 初始化你的状态变量
        self.pending_bis: List[Bi] = []
    
    def update(self, bi: Bi):
        """
        每添加一笔时调用
        参数:
            bi: 最新的笔
        """
        self.pending_bis.append(bi)
        
        # 尝试形成新线段
        if self._can_form_segment():
            self._create_segment()
    
    def _can_form_segment(self) -> bool:
        """判断是否可以形成线段"""
        # 至少需要3笔
        if len(self.pending_bis) < 3:
            return False
        
        # 实现你的判断逻辑
        # ...
        
        return True
    
    def _create_segment(self):
        """创建新线段"""
        # 确定起始笔和结束笔
        start_bi = self.pending_bis[0]
        end_bi = self.pending_bis[-1]
        
        # 创建线段
        seg = Seg(
            idx=len(self.lst),
            start_bi=start_bi,
            end_bi=end_bi,
            is_sure=True,
            seg_dir=start_bi.dir,
            lv=self.lv,
        )
        
        # 设置笔的线段归属
        bi = start_bi
        while bi and bi.idx <= end_bi.idx:
            bi.set_seg_idx(seg.idx)
            bi.parent_seg = seg
            bi = bi.next
        
        # 添加到列表
        self.lst.append(seg)
        
        # 清空待处理的笔
        self.pending_bis = [end_bi]
```

### 2. 注册新算法

修改 `kline/kline_list.py`:

```python
def _get_seg_list_cls(self):
    if self.conf.seg_conf.seg_algo == "chan":
        from seg.seg_list_chan import SegListChan
        return SegListChan
    elif self.conf.seg_conf.seg_algo == "1+1":
        from seg.seg_list_dyh import SegListDYH
        return SegListDYH
    elif self.conf.seg_conf.seg_algo == "break":
        from seg.seg_list_def import SegListDef
        return SegListDef
    elif self.conf.seg_conf.seg_algo == "custom":  # 新增
        from seg.seg_list_custom import SegListCustom
        return SegListCustom
    else:
        raise Exception(f"Unknown seg_algo: {self.conf.seg_conf.seg_algo}")
```

### 3. 使用新算法

```python
config = ChanConfig({
    "seg_algo": "custom",
})

chan = Chan(..., config=config)
```

---

## 算法示例: 简单突破算法

```python
# seg/seg_list_simple.py

from bi.bi import Bi
from common.enums import BI_DIR
from seg.seg import Seg
from seg.seg_list_comm import SegListComm


class SegListSimple(SegListComm):
    """
    简单突破算法:
    当一笔突破前一线段的端点时，前一线段结束
    """
    
    def __init__(self, seg_config, lv):
        super().__init__(seg_config, lv)
        self.current_seg_start: Bi = None
        self.current_high = float('-inf')
        self.current_low = float('inf')
    
    def update(self, bi: Bi):
        # 第一笔，开始新线段
        if self.current_seg_start is None:
            self.current_seg_start = bi
            self._update_extreme(bi)
            return
        
        # 检查是否突破
        if self._is_breakout(bi):
            self._finalize_segment(bi.pre)
            self.current_seg_start = bi
            self._reset_extreme()
            self._update_extreme(bi)
        else:
            self._update_extreme(bi)
    
    def _is_breakout(self, bi: Bi) -> bool:
        """检查是否突破"""
        seg_dir = self.current_seg_start.dir
        
        if seg_dir == BI_DIR.UP:
            # 上升线段，下跌笔突破最低点
            if bi.is_down() and bi.get_end_val() < self.current_low:
                return True
        else:
            # 下降线段，上涨笔突破最高点
            if bi.is_up() and bi.get_end_val() > self.current_high:
                return True
        
        return False
    
    def _update_extreme(self, bi: Bi):
        """更新极值"""
        self.current_high = max(self.current_high, bi._high())
        self.current_low = min(self.current_low, bi._low())
    
    def _reset_extreme(self):
        """重置极值"""
        self.current_high = float('-inf')
        self.current_low = float('inf')
    
    def _finalize_segment(self, end_bi: Bi):
        """完成线段"""
        seg = Seg(
            idx=len(self.lst),
            start_bi=self.current_seg_start,
            end_bi=end_bi,
            is_sure=True,
            seg_dir=self.current_seg_start.dir,
            lv=self.lv,
        )
        
        # 设置笔归属
        bi = self.current_seg_start
        while bi and bi.idx <= end_bi.idx:
            bi.set_seg_idx(seg.idx)
            bi.parent_seg = seg
            bi = bi.next
        
        self.lst.append(seg)
```

---

## 处理虚线段

线段可能是"虚"的（未确定）：

```python
def update(self, bi: Bi):
    # ...
    
    # 创建虚线段
    seg = Seg(..., is_sure=False)
    
    # 后续如果确定了，更新状态
    def confirm_segment(self):
        if self.lst and not self.lst[-1].is_sure:
            self.lst[-1].is_sure = True
```

---

## 继承 SegListComm 的好处

基类提供了很多实用方法：

```python
# 添加线段
self.add_new_seg(start_bi, end_bi, is_sure, seg_dir, reason)

# 处理剩余笔
self.collect_left_seg(bi_list)

# 更新最后一个虚线段
self.update_last_seg(new_end_bi)
```

---

## 注意事项

1. **笔的归属**: 每笔必须设置 `seg_idx` 和 `parent_seg`
2. **双向链表**: 确保线段的 `pre` 和 `next` 正确
3. **虚线段**: 正确处理未确定的线段
4. **中枢计算**: 线段完成后会自动计算中枢
5. **性能**: 避免在 `update` 中做过多计算

---

## 下一步

- [代码规范](./04-code-style.md) - 编码约定
- [完整版功能](../07-full-version/) - 了解完整版架构


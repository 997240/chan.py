# 代码规范

## 命名约定

### 文件命名

- 使用小写字母和下划线
- 示例: `bi_list.py`, `kline_unit.py`

### 类命名

- 使用 PascalCase
- 示例: `BiList`, `KLineUnit`, `ChanConfig`

### 函数/方法命名

- 使用 snake_case
- 私有方法以单下划线开头
- 示例: `get_kl_data()`, `_fetch_data()`

### 变量命名

| 类型 | 约定 | 示例 |
|------|------|------|
| 普通变量 | snake_case | `bi_list`, `seg_idx` |
| 常量 | UPPER_CASE | `MAX_KL_CNT` |
| 私有属性 | 单下划线 | `_cache` |
| 内部属性 | 双下划线 | `__dir` |

---

## 常用缩写

| 缩写 | 全称 | 说明 |
|------|------|------|
| klu | KLine Unit | 单根K线 |
| klc | KLine Combine | 合并K线 |
| bi | Bi | 笔 |
| seg | Segment | 线段 |
| zs | Zhongshu | 中枢 |
| bsp | Buy Sell Point | 买卖点 |
| cbsp | Custom BSP | 自定义买卖点 |
| fx | Fractal | 分形 |
| lv | Level | 级别 |
| conf | Config | 配置 |

---

## 代码结构

### 类的组织顺序

```python
class MyClass:
    # 1. 类变量
    _class_var = None
    
    # 2. __init__
    def __init__(self, ...):
        pass
    
    # 3. 属性 (@property)
    @property
    def my_property(self):
        pass
    
    # 4. 公开方法
    def public_method(self):
        pass
    
    # 5. 私有方法
    def _private_method(self):
        pass
    
    # 6. 类方法
    @classmethod
    def class_method(cls):
        pass
    
    # 7. 静态方法
    @staticmethod
    def static_method():
        pass
```

### 导入顺序

```python
# 1. 标准库
import copy
import datetime
from typing import List, Optional

# 2. 项目内部模块
from common.enums import KL_TYPE, BI_DIR
from common.chan_exception import ChanException
from bi.bi import Bi
```

---

## 类型注解

### 推荐使用类型注解

```python
from typing import List, Optional, Dict, Union

def get_bi_list(self) -> List[Bi]:
    pass

def find_bi(self, idx: int) -> Optional[Bi]:
    pass

def process(self, data: Union[str, int]) -> Dict[str, float]:
    pass
```

### 复杂类型

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from seg.seg import Seg

class Bi:
    parent_seg: Optional['Seg'] = None  # 前向引用
```

---

## 缓存使用

### @make_cache 装饰器

对于计算密集的方法，使用缓存：

```python
from common.cache import make_cache

class Bi:
    @make_cache
    def get_begin_val(self):
        """这个方法的结果会被缓存"""
        return self.begin_klc.low if self.is_up() else self.begin_klc.high
    
    def clean_cache(self):
        """数据更新后需要清除缓存"""
        self._memoize_cache = {}
```

### 缓存清除

当对象状态改变时，清除缓存：

```python
def update_end(self, new_end):
    self.__end_klc = new_end
    self.clean_cache()  # 清除缓存
```

---

## 异常处理

### 使用项目异常类

```python
from common.chan_exception import ChanException, ErrCode

# 抛出异常
if not valid:
    raise ChanException("描述信息", ErrCode.PARA_ERROR)

# 捕获异常
try:
    process()
except ChanException as e:
    if e.errcode == ErrCode.NO_DATA:
        handle_no_data()
    else:
        raise
```

### 常用错误码

| 错误码 | 说明 |
|--------|------|
| PARA_ERROR | 参数错误 |
| CONFIG_ERROR | 配置错误 |
| NO_DATA | 无数据 |
| SRC_DATA_NOT_FOUND | 数据源未找到 |
| BI_ERR | 笔计算错误 |
| SEG_ERR | 线段计算错误 |

---

## 文档字符串

### 类文档

```python
class BiList:
    """
    笔列表类
    
    管理笔的创建、更新和查询。
    
    Attributes:
        bi_list: 笔的列表
        config: 笔的配置
    """
```

### 方法文档

```python
def can_make_bi(self, klc: KLine, last_end: KLine, for_virtual: bool = False) -> bool:
    """
    判断是否可以成笔
    
    Args:
        klc: 当前合并K线
        last_end: 上一个端点
        for_virtual: 是否用于虚笔判断
    
    Returns:
        是否可以成笔
    
    Raises:
        ChanException: 当参数无效时
    """
```

---

## 测试

### 命名约定

```python
# test_bi.py

def test_bi_direction():
    """测试笔方向判断"""
    pass

def test_bi_amplitude():
    """测试笔振幅计算"""
    pass
```

### 断言使用

```python
# 使用 assert（开发时）
assert bi.is_up(), "笔应该是上升的"

# 使用项目异常（生产代码）
if not bi.is_up():
    raise ChanException("笔方向错误", ErrCode.BI_ERR)
```

---

## Git 提交

### 提交信息格式

```
<type>: <subject>

<body>
```

### Type 类型

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | 修复bug |
| docs | 文档更新 |
| refactor | 重构 |
| test | 测试 |
| chore | 杂项 |

### 示例

```
feat: 添加RSI指标支持

- 新增 math_util/rsi.py
- 在 ChanConfig 中添加 cal_rsi 配置
- 在 KLineUnit 中添加 rsi 属性
```

---

## 性能建议

1. **避免重复计算**: 使用 `@make_cache`
2. **生成器替代列表**: 大数据用 `yield`
3. **延迟导入**: 避免循环导入
4. **批量处理**: 尽量批量而非逐个处理

---

## 下一步

- [完整版功能](../07-full-version/) - 了解完整版架构
- [FAQ](../08-faq/faq.md) - 常见问题


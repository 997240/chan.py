# 环境安装

## 系统要求

| 要求 | 说明 |
|------|------|
| Python | 3.8+ (推荐 3.11+) |
| 操作系统 | Windows / macOS / Linux |
| 内存 | 建议 4GB+ |

---

## 安装步骤

### 1. 克隆项目

```bash
git clone https://github.com/Vespa314/chan.py.git
cd chan.py
```

### 2. 创建虚拟环境（推荐）

```bash
# 使用 venv
python -m venv venv

# Windows 激活
venv\Scripts\activate

# macOS/Linux 激活
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r script/requirements.txt
```

主要依赖包：

| 包名 | 用途 |
|------|------|
| matplotlib | 绑图 |
| baostock | A股数据源 |
| ccxt | 数字货币数据 |
| futu-api | 富途数据/交易 |

---

## Python 版本兼容性

### 问题：`Self` 类型不兼容

如果你使用的是 **Python 3.10 或更低版本**，可能会遇到以下错误：

```
ImportError: cannot import name 'Self' from 'typing'
```

**原因**: `Self` 类型是 Python 3.11 新增的。

**解决方案**:

方案一：升级到 Python 3.11+（推荐）

```bash
# 使用 pyenv 或 conda 安装 Python 3.11
conda create -n chan python=3.11
conda activate chan
```

方案二：安装 typing_extensions 并修改代码

```bash
pip install typing_extensions
```

然后将代码中的：
```python
from typing import Self
```

修改为：
```python
from typing_extensions import Self
```

涉及的文件包括：
- `seg/eigen.py`
- `seg/seg.py`
- `combiner/kline_combiner.py`
- 等

---

## 数据源配置

### BaoStock（A股，免费）

```bash
pip install baostock
```

无需额外配置，直接使用。

### CSV 本地数据

准备 CSV 文件，格式要求：

```csv
time_key,open,high,low,close,volume,turnover,turnover_rate
2023-01-01,10.0,10.5,9.8,10.2,1000000,10000000,0.5
```

### CCXT（数字货币）

```bash
pip install ccxt
```

### Futu（港美股）

```bash
pip install futu-api
```

需要安装并运行 FutuOpenD 客户端。

---

## 验证安装

创建测试脚本 `test_install.py`：

```python
# 测试基础导入
try:
    from chan import Chan
    from chan_config import ChanConfig
    from common.enums import DATA_SRC, KL_TYPE
    print("✅ 核心模块导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")

# 测试数据源
try:
    import baostock
    print("✅ baostock 可用")
except ImportError:
    print("⚠️ baostock 未安装（A股数据不可用）")

try:
    import matplotlib
    print("✅ matplotlib 可用")
except ImportError:
    print("❌ matplotlib 未安装（绑图不可用）")

print("\n安装验证完成！")
```

运行：

```bash
python test_install.py
```

---

## 常见安装问题

### 1. pip 安装超时

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. matplotlib 显示问题

Windows 用户可能需要指定后端：

```python
import matplotlib
matplotlib.use('TkAgg')  # 或 'Qt5Agg'
```

### 3. baostock 登录失败

```python
import baostock as bs
bs.login()  # 需要在交易日的交易时间内
```

---

## 下一步

- [第一个Demo](./03-first-demo.md) - 运行示例代码


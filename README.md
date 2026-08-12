# ClickClock

ClickClock 是一个轻量级的数字电路仿真器，使用自定义的硬件描述语言（`.clk`）来描述和仿真数字电路。

## 特性

- 自定义硬件描述语言，支持模块化设计
- 预处理阶段展开 `use` 文件包含
- 支持宏定义和宏展开
- 组合逻辑自动拓扑排序
- 时序逻辑周期仿真
- 内建模块：`dff`（D触发器）、`not`、`and`、`or`、`xor`、`nand`、`nor`、`xnor`、`mux`、`add` 等
- 支持信号切片（位选取）

## 快速开始

### 系统要求

- Python 3.12.8 或更高版本

### 安装

```bash
git clone https://github.com/Rain888-123/ClickClock.git
cd clickclock
uv sync  # 或 pip install -e .
```

### 运行示例
```bash
uv run clickclock  # 或 clickclock
```

### 编写你的第一个电路

在项目根目录创建 `test` 目录，创建一个 `test.clk` 文件在此目录下：

```text
module program_counter[8]:  # module 模块名[位宽]:
    input en[1], data[8]
    output out[256] <- cnt.q
    add inc[8]:
        a=cnt.q
        b=1
        cin=0
    dff cnt[8]:
        we=1
        d=m.out
    mux m[8]:  # 这是一行注释
        sel=en
        a=inc.sum
        b=data

# 你好，这是末尾

```

## 语言参考

### 模块定义

```text
module module_name[width]:
input port_name[width]
output port_name[width] <- source_signal
...
```

### 实例化

```text
module_type instance_name[width]:
port_name = signal_or_value
```

### 文件包含

```text
use std, mylib
```

### 宏定义

```text
MACRO := value
```

## 项目架构

```text
clickclock/
├── src/
│   └── clickclock/
│       ├── __init__.py      # 入口，组装各模块
│       ├── loader.py        # 文件 I/O
│       ├── preproc.py       # 预处理：展开 use
│       ├── lexer.py         # 词法分析
│       ├── parser.py        # 语法分析
│       ├── simulator.py     # 仿真器
│       └── errors.py        # 错误处理
├── config/
│   ├── modules.toml         # 内建模块定义
│   └── lib.py               # 求值函数
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
└── uv.lock
```

## 内建模块
详见 [modules.toml](config/modules.toml) 。

## 许可证

本项目采用 GNU General Public License v3.0 或更高版本。

详见 [LICENSE](LICENSE) 。

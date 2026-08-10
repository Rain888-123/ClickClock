# src/clickclock/__init__.py


from .lexer import preprocess
from .parser import parse
from .simulator import Simulator


def load_config(path = "config/modules.toml") -> dict[str, str|list[str]|bool]:
    from pathlib import Path
    from tomllib import load
    with open(Path(__file__).parent.parent.parent / path, "rb") as f:
        return load(f)


def main() -> None:
    test = '''# 使用标准库
use std

module program_counter[32]: # module 模块名[位宽]:
    input en[1], data[32]
    output out[32] <- cnt.q
    
    add add4[32]:
        a=cnt.q
        b=4
        cin=0
    mux m[32]: # 这是一行注释
        sel=en
        a=add4.sum
        b=data
    dff cnt[32]:
        we=1
        d=m.out

# 你好，这是末尾
        '''
    ast = parse(preprocess(test))
    sim = Simulator(ast, load_config())
    for module in ast.modules:
        sim.init(module)
        for _ in range(10):
            sim.step(module)
            print(sim.top_signals)
            print(sim.inst_signals)
            print()

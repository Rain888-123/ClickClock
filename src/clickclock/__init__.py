# src/clickclock/__init__.py


from .parser import parse
from .lexer import preprocess

test = '''true := ON
clk := 10000

# 使用标准库
use std

module program_counter[32]: # module 模块名[位宽]:
    input en[1], data[32]
    output out[32] <- cnt.q

    mux m[32]: # 这是一行注释
        sel=en
        a=add.out
        b=data
    dff cnt[32]:
        init 0x80000000
        we=true
        d=mux.out
    add add4[32]:
        a=cnt.q
        b=4
        cin=OFF

# 你好，这是末尾
    '''


def main():
    result = parse(preprocess(test))
    print("\n解析结果：")
    print(f"引用库：{result.uses}")
    for mod in result.modules:
        print(f"模块：{mod.name}[{mod.width}]")
        print(f"\t输入：{[f'{i.name}[{i.width}]' for i in mod.inputs]}")
        print(f"\t输出：{[f'{o.name}[{o.width}] <- {o.source}' for o in mod.outputs]}")
        for inst in mod.instances:
            print(f"\t例化：{inst.mod_name} {inst.name}[{inst.width}]", end="")
            if inst.init is not None:
                print(f" init={hex(inst.init)}", end="")
            print()
            for port, sig in inst.port_map:
                print(f"\t\t{port} = {sig}")

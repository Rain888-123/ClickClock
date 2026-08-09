import re


class Node:
    def __init__(self, name, width=1) -> None:
        self.name = name
        self.width = width


class AST:
    class Module(Node):
        class Input(Node):
            def __init__(self, name, width=1) -> None:
                super().__init__(name, width)
        
        
        class Output(Node):
            def __init__(self, name, source, width=1) -> None:
                super().__init__(name, width)
                self.source = source
        
        
        def __init__(self, name, width=1) -> None:
            super().__init__(name, width)
            self.inputs = []
            self.outputs = []
            self.instances = []
    
    
    class Instance(Node):
        def __init__(self, name, width=1) -> None:
            super().__init__(name, width)
            self.mod_name = ""
            self.port_map = []
            self.init = None
    
    
    def __init__(self) -> None:
        self.macros = {}
        self.modules = []
        self.uses = []


def error(msg, index, line) -> None:
    raise SyntaxError(f"{msg}, 第 {index} 行, {line.lstrip()}")


def parse(text) -> AST:
    # 处理文本
    lines = {}
    for index, line in enumerate(text.splitlines(), start=1):
        line = line.expandtabs(4)
        idx = line.find("#")
        code = line.rstrip() if idx == -1 else line[:idx].rstrip()
        if not code:
            continue
        lines[index] = code
    
    # 构建抽象语法树
    ast = AST()
    cur_mod = None
    cur_inst = None
    stack = [0]
    macro_allowed = True
    
    for index, line in lines.items():
        # 处理缩进
        indent = len(line) - len(line.lstrip())
        if indent % 4 != 0:
            error(f"缩进的空格数应为 4 的倍数，但行前有 {indent} 个空格", index, line)
        indent //= 4
        
        # 更新缩进栈
        while stack and indent < stack[-1]:
            stack.pop()
            if len(stack) == 1:  # 回到顶层
                cur_mod = None
                cur_inst = None
            elif len(stack) == 2:  # 回到模块层
                cur_inst = None
        if indent > stack[-1]:
            stack.append(indent)
        
        words = line.lstrip().split()
        first = words[0]
        others = " ".join(words[1:])
        
        # 宏定义
        if ":=" in line:
            if not macro_allowed:
                error("宏只能在文件开头定义", index, line)
            if indent != 0:
                error("宏定义必须在顶层", index, line)
            key, value = line.lstrip().split(":=", 1)
            key = key.strip()
            value = value.strip()
            if not re.match(r'^\w+$', key):
                error(f"非法宏名 {key}", index, line)
            if key in ast.macros:
                error(f"宏 {key} 重复定义", index, line)
            ast.macros[key] = value
            continue
        
        # 遇到非宏行，禁止后续再定义宏
        macro_allowed = False
        
        if first == "module":
            match = re.match(r'([a-zA-Z_]\w*)\[(\d+)]:', others)
            if not match:
                error("模块定义格式错误", index, line)
            new_mod = AST.Module(match.group(1), int(match.group(2)))
            ast.modules.append(new_mod)
            cur_mod = new_mod
            cur_inst = None
        
        elif first == "use":
            items = [item.strip() for item in others.split(",") if item.strip()]
            for item in items:
                if item not in ast.uses:
                    ast.uses.append(item)
        
        elif cur_mod is not None and first == "input":
            matches = re.findall(r'(\w+)\[(\d+)]', others)
            if not matches:
                error("输入端口格式错误", index, line)
            cur_mod.inputs.extend([cur_mod.Input(name, int(width)) for name, width in matches])
        
        elif cur_mod is not None and first == "output":
            matches = re.findall(r'(\w+)\[(\d+)]\s*<-\s*([\w\[\].]+)', others)
            if not matches:
               error("输出端口格式错误", index, line)
            cur_mod.outputs.extend([cur_mod.Output(name, source, int(width)) for name, width, source in matches])
        
        elif cur_mod is not None and first == "init":
            if cur_inst is None:
                error("init 必须在例化语句之后", index, line)
            cur_inst.init = int(others, 0)
        
        elif cur_mod is not None:
            # 尝试匹配子模块例化
            match = re.match(r'([a-zA-Z_]\w*)\s+([a-zA-Z_]\w*)\[(\d+)]:', line.lstrip())
            if match:
                mod_name = match.group(1)
                inst_name = match.group(2)
                width = int(match.group(3))
                ins = AST.Instance(inst_name, width)
                ins.mod_name = mod_name
                cur_mod.instances.append(ins)
                cur_inst = ins
            else:
                # 端口映射: port=signal
                stripped = line.lstrip()
                eq_pos = stripped.find("=")
                if eq_pos == -1:
                    error("端口映射格式错误", index, line)
                port_name = stripped[:eq_pos].strip()
                signal = stripped[eq_pos + 1:].strip()
                    
                # 检查等号数量，避免歧义
                if signal.count("=") > 0:
                   error("端口映射值应只包含 1 个等号", index, line)
                    
                if cur_inst is None:
                    error("端口映射必须在例化语句之后", index, line)
                cur_inst.port_map.append((port_name, signal))
        else:
            error("非法代码", index, line)
    
    return ast


if __name__ == "__main__":
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
    result = parse(test)
    print("\n解析结果：")
    print(f"宏定义：{result.macros}")
    print(f"引用库：{result.uses}")
    for mod in result.modules:
        print(f"\n模块：{mod.name}[{mod.width}]")
        print(f"\t输入：{[f'{i.name}[{i.width}]' for i in mod.inputs]}")
        print(f"\t输出：{[f'{o.name}[{o.width}] <- {o.source}' for o in mod.outputs]}")
        for inst in mod.instances:
            print(f"\t例化：{inst.mod_name} {inst.name}[{inst.width}]", end="")
            if inst.init is not None:
                print(f" init={hex(inst.init)}", end="")
            print()
            for port, sig in inst.port_map:
                print(f"\t\t{port} = {sig}")

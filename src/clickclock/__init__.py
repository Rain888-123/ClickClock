# src/clickclock/__init__.py


from .loader import load_source, load_config
from .lexer import preprocess
from .parser import parse
from .simulator import Simulator


def main() -> None:
    ast = parse(preprocess(load_source("test", "test")))
    sim = Simulator(ast, load_config("modules"))
    target_cycles = 100
    for module in ast.modules:
        sim.init(module)
    for _ in range(target_cycles):
        for module in ast.modules:
            sim.step(module)
            print(sim.cycle)
            print(sim.top)
            print(sim.inst)
            print()

# src/clickclock/__init__.py


from . import loader
from .preproc import expand
from .lexer import tokenize
from .parser import parse
from .simulator import Simulator


def main() -> None:
    text = expand(loader.source("test", "test"), "test")
    ast = parse(tokenize(text))
    sim = Simulator(ast, loader.config("modules"), loader.lib("lib").EVAL_MAP)
    target_cycles = 256
    for module in ast.modules:
        sim.init(module)
    for _ in range(target_cycles):
        for module in ast.modules:
            sim.step(module)
            print(sim.cycle)
            print(sim.top)
            print(sim.inst)
            print()

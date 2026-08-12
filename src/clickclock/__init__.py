# src/clickclock/__init__.py

# Copyright (C) 2026 Rain888
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from . import loader
from .preproc import expand
from .lexer import tokenize
from .parser import parse
from .simulator import Simulator


def gui() -> None:
    pass


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

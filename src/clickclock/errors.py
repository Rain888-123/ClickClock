# src/clickclock/errors.py

# Copyright (C) 2026 Rain888
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

def line_error(msg, index, line) -> None:
    raise SyntaxError(f"{msg}, 第 {index} 行, {line.lstrip()}")


def value_error(msg, something) -> None:
    raise ValueError(f"{msg}，{something}")


def file_error(path) -> None:
    raise FileNotFoundError(f"找不到文件 {path}")

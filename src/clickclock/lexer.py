# src/clickclock/lexer.py

# Copyright (C) 2026 Rain888
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

import re
from .errors import line_error


def tokenize(text) -> list[tuple[int, str, int]]:
	lines = []
	macros = {}
	macro_allowed = True
	
	for index, line in enumerate(text.splitlines(), start=1):
		# 展开tab、去注释、去空行
		line = line.expandtabs(4)
		idx = line.find("#")
		code = line.rstrip() if idx == -1 else line[:idx].rstrip()
		if not code:
			continue
		
		# 计算缩进
		stripped = code.lstrip()
		indent = len(code) - len(stripped)
		if indent % 4 != 0:
			line_error(f"缩进的空格数应为 4 的倍数，但行前有 {indent} 个空格", index, line)
		indent_level = indent // 4
		
		# 处理宏定义
		if ":=" in stripped:
			if not macro_allowed:
				line_error("宏只能在文件开头定义", index, line)
			if indent_level != 0:
				line_error("宏定义应该只在顶层出现", index, line)
			key, value = stripped.split(":=", 1)
			key = key.strip()
			value = value.strip()
			if not re.match(r'^\w+$', key):
				line_error(f"非法宏名 {key}", index, line)
			if key in macros:
				line_error(f"宏 {key} 重复定义", index, line)
			macros[key] = value
			continue  # 宏定义行不加入代码行列表
		
		# 遇到非宏行，禁止后续再定义宏
		macro_allowed = False
		
		# 宏展开
		for key, val in macros.items():
			stripped = re.sub(r'\b' + re.escape(key) + r'\b', val, stripped)
		
		lines.append((index, stripped, indent_level))
	
	return lines

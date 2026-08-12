# src/clickclock/loader.py

# Copyright (C) 2026 Rain888
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from pathlib import Path
from types import ModuleType
from .errors import file_error


def source(name, base_dir = ".") -> str:
	path = Path(base_dir) / f"{name}.clk"
	if not path.exists():
		raise file_error(path)
	
	return path.read_text(encoding="utf-8")


def config(name, base_dir = "config") -> dict[str, str|list|bool]:
	path = Path(base_dir) / f"{name}.toml"
	if not path.exists():
		raise file_error(path)
	from tomllib import load
	
	with open(path, "rb") as f:
		return load(f)


def lib(name, base_dir = "config") -> ModuleType:
	import sys
	import importlib.util
	
	path = Path(base_dir) / f"{name}.py"
	if not path.exists():
		file_error(path)
	
	spec = importlib.util.spec_from_file_location(name, str(path))
	module = importlib.util.module_from_spec(spec)
	sys.modules[name] = module
	spec.loader.exec_module(module)
	return module
	
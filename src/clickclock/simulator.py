# src/clickclock/simulator.py

# Copyright (C) 2026 Rain888
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from .errors import value_error

SEQUENTIAL = True
IN = 0
OUT = 1


class Simulator:
	def __init__(self, ast, all_modules, eval_map) -> None:
		self.ast = ast
		self.top = {}, {}
		self.inst = {}, {}
		self.sorted_insts = None
		self.all_modules = all_modules
		self.eval_map = eval_map
		self.cycle = 0
	
	def init(self, mod) -> None:
		self.top[IN].clear()
		self.top[OUT].clear()
		self.inst[IN].clear()
		self.inst[OUT].clear()
		self.sorted_insts = self._topological_sort(mod)
		
		for inp in mod.inputs:
			self.top[IN][inp.name] = 0
		for out in mod.outputs:
			self.top[OUT][out.name] = 0
			
		for inst in mod.instances:
			mod_def = self.all_modules.get(inst.mod_name)
			if mod_def is None:
				value_error("未知模块类型", inst.mod_name)
			for inp in mod_def["inputs"]:
				self.inst[IN][f"{inst.name}.{inp}"] = 0
			for out in mod_def["outputs"]:
				self.inst[OUT][f"{inst.name}.{out}"] = 0
	
	def _get(self, expr, slice_info = None) -> int:
		try:
			return int(expr, 0)
		except ValueError:
			pass
		
		value = 0
		if expr in self.inst[OUT]:  # 实例输出
			value = self.inst[OUT][expr]
		elif expr in self.top[IN]:  # 顶层输入
			value = self.top[IN][expr]
		elif expr in self.top[OUT]:  # 顶层输出
			value = self.top[OUT][expr]
		else:  # 未找到
			value_error("未知信号", expr)
			return value
		
		if slice_info:
			high, low = slice_info
			w = high - low + 1
			return (value >> low) & ((1 << w) - 1)
		return value
	
	def _topological_sort(self, mod) -> list:
		# 构建依赖图
		comb_insts = [
			inst for inst in mod.instances if not self.all_modules.get(inst.mod_name, {}).get("sequential", False)
		]
		depends_on = {}
		for inst in comb_insts:
			deps = set()
			for port_name, signal_expr, _ in inst.port_map:
				if signal_expr and '.' in signal_expr:
					upstream_name = signal_expr.split('.')[0]
					upstream_inst = next((i for i in comb_insts if i.name == upstream_name), None)
					if upstream_inst and upstream_name != inst.name:  # 排除自依赖
						deps.add(upstream_name)
			depends_on[inst.name] = deps
		
		# Kahn 拓扑排序
		no_deps = [inst for inst in comb_insts if not depends_on.get(inst.name, set())]
		temp_deps = {name: set(deps) for name, deps in depends_on.items()}
		sorted_insts = []
		
		while no_deps:
			inst = no_deps.pop(0)
			sorted_insts.append(inst)
			# 移除该实例对其他实例的依赖
			for other_inst in mod.instances:
				if other_inst.name in temp_deps and inst.name in temp_deps[other_inst.name]:
					temp_deps[other_inst.name].remove(inst.name)
					if not temp_deps[other_inst.name]:
						no_deps.append(other_inst)
		
		# 检查是否有环
		if len(sorted_insts) != len(comb_insts):
			value_error("组合逻辑中存在环路", mod.name)
		
		# 将时序实例追加到末尾
		seq_insts = [inst for inst in mod.instances if inst not in comb_insts]
		sorted_insts.extend(seq_insts)
		
		return sorted_insts
	
	def _step(self, mod, mode = not SEQUENTIAL) -> None:
		insts = self.sorted_insts if not mode else mod.instances
		for inst in insts:
			mod_def = self.all_modules.get(inst.mod_name)
			if not mod_def:
				value_error("未知模块类型", inst.mod_name)
			if mode != mod_def.get("sequential", not SEQUENTIAL):
				continue
				
			# 检查端口映射是否有未知端口
			for port_name, _, _ in inst.port_map:
				if port_name not in mod_def["inputs"] and port_name not in mod_def.get("outputs", []):
					value_error(f"模块 {inst.mod_name} 无此端口", port_name)
			
			# 收集输入值
			args = []
			for port_name in mod_def["inputs"]:
				matched = [(sig, slc) for p, sig, slc in inst.port_map if p == port_name]
				if matched:
					signal_expr, slice_info = matched[0]
				else:
					signal_expr, slice_info = None, None
				
				if signal_expr:
					args.append(self._get(signal_expr, slice_info))
				else:
					args.append(0)
			if mode:
				prev = self.inst[OUT].get(f"{inst.name}.{mod_def["outputs"][0]}", 0)
				args.append(prev)
			args.append(inst.width)
			
			# 同步更新实例输入
			for i, port_name in enumerate(mod_def["inputs"]):
				self.inst[IN][f"{inst.name}.{port_name}"] = args[i]
			
			# 调用求值函数
			func = self.eval_map.get(inst.mod_name)
			if func is None:
				value_error("未知子模块类型", inst.mod_name)
			result = func(*args)
			
			# 写回输出
			if isinstance(result, tuple):
				for i, port_name in enumerate(mod_def["outputs"]):
					self.inst[OUT][f"{inst.name}.{port_name}"] = result[i]
			else:
				for port_name in mod_def["outputs"]:
					self.inst[OUT][f"{inst.name}.{port_name}"] = result
	
	def step(self, mod) -> None:
		self._step(mod)
		self._step(mod, SEQUENTIAL)
		
		# 更新顶层输出
		for out in mod.outputs:
			self.top[OUT][out.name] = self._get(out.source, out.slice_info)
		
		# 步进一个周期
		self.cycle += 1

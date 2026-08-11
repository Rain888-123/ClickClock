# src/clickclock/simulator.py


from .errors import value_error
from .lib import EVAL_MAP


class Simulator:
	def __init__(self, ast, config) -> None:
		self.ast = ast
		self.top = {}, {}
		self.inst = {}, {}
		self.config = config
	
	def init(self, mod) -> None:
		self.top[0].clear()
		self.top[1].clear()
		self.inst[0].clear()
		self.inst[1].clear()
		
		for inp in mod.inputs:
			self.top[0][inp.name] = 0
		for out in mod.outputs:
			self.top[1][out.name] = 0
			
		for inst in mod.instances:
			mod_def = self.config.get(inst.mod_name)
			if not mod_def:
				value_error("未知模块类型", inst.mod_name)
			for inp in mod_def["inputs"]:
				self.inst[0][f"{inst.name}.{inp}"] = 0
			for out in mod_def["outputs"]:
				self.inst[1][f"{inst.name}.{out}"] = 0
	
	def _get(self, expr) -> int:
		try:
			return int(expr, 0)
		except ValueError:
			pass
		
		# 实例输出
		if expr in self.inst[1]:
			return self.inst[1][expr]
		# 顶层输入
		if expr in self.top[0]:
			return self.top[0][expr]
		# 顶层输出
		if expr in self.top[1]:
			return self.top[1][expr]
		# 未找到
		value_error("未知信号", expr)
		return 0
		
	
	def step(self, mod) -> None:
		# 组合逻辑
		for inst in mod.instances:
			mod_def = self.config.get(inst.mod_name)
			if not mod_def:
				value_error("未知模块类型", inst.mod_name)
			if mod_def.get("sequential"):
				continue
			
			# 收集输入值
			args = []
			for port_name in mod_def["inputs"]:
				signal_expr = next((sig for p, sig in inst.port_map if p == port_name), None)
				if signal_expr:
					args.append(self._get(signal_expr))
				else:
					args.append(0)
			args.append(inst.width)
			# 同步更新 inst_signals[0]
			for i, port_name in enumerate(mod_def["inputs"]):
				self.inst[0][f"{inst.name}.{port_name}"] = args[i]
			
			# 调用求值函数
			func = EVAL_MAP.get(inst.mod_name)
			if not func:
				value_error("未知子模块类型", inst.mod_name)
			result = func(*args)
			
			# 写回输出
			if isinstance(result, tuple):
				for i, port_name in enumerate(mod_def["outputs"]):
					self.inst[1][f"{inst.name}.{port_name}"] = result[i]
			else:
				for port_name in mod_def["outputs"]:
					self.inst[1][f"{inst.name}.{port_name}"] = result
		
		# 时序逻辑
		for inst in mod.instances:
			mod_def = self.config.get(inst.mod_name)
			if not mod_def:
				value_error("未知模块类型", inst.mod_name)
			if not mod_def.get("sequential"):
				continue
			
			# 收集输入值
			args = []
			for port_name in mod_def["inputs"]:
				signal_expr = next((sig for p, sig in inst.port_map if p == port_name), None)
				if signal_expr:
					args.append(self._get(signal_expr))
				else:
					args.append(0)
			prev = self.inst[1].get(f"{inst.name}.{mod_def["outputs"][0]}", 0)
			args.append(prev)
			args.append(inst.width)
			# 同步更新 inst_signals[0]
			for i, port_name in enumerate(mod_def["inputs"]):
				self.inst[0][f"{inst.name}.{port_name}"] = args[i]
			
			# 调用求值函数
			func = EVAL_MAP.get(inst.mod_name)
			if not func:
				value_error("未知子模块类型", inst.mod_name)
			result = func(*args)
			
			# 写回输出
			if isinstance(result, tuple):
				for i, port_name in enumerate(mod_def["outputs"]):
					self.inst[1][f"{inst.name}.{port_name}"] = result[i]
			else:
				for port_name in mod_def["outputs"]:
					self.inst[1][f"{inst.name}.{port_name}"] = result
				
		# 更新顶层输出
		for out in mod.outputs:
			self.top[1][out.name] = self._get(out.source)

# src/clickclock/parser.py


import re
from .errors import line_error, value_error


class Node:
	def __init__(self, name, width) -> None:
		self.name = name
		self.width = width


class AST:
	class Module(Node):
		class Input(Node):
			def __init__(self, name, width) -> None:
				super().__init__(name, width)
		
		
		class Output(Node):
			def __init__(self, name, width, source, slice_info) -> None:
				super().__init__(name, width)
				self.source = source
				self.slice_info = slice_info
		
		
		def __init__(self, name, width) -> None:
			super().__init__(name, width)
			self.inputs = []
			self.outputs = []
			self.instances = []
	
	
	class Instance(Node):
		def __init__(self, name, width) -> None:
			super().__init__(name, width)
			self.mod_name = ""
			self.port_map = []
	
	
	def __init__(self) -> None:
		self.modules = []


class IndentState:
	def __init__(self) -> None:
		self.stack = [0]
		self.cur_mod = None
		self.cur_inst = None
	
	def update(self, indent) -> None:
		# 更新缩进栈
		while self.stack and indent < self.stack[-1]:
			self.stack.pop()
			if len(self.stack) == 1:  # 回到顶层
				self.cur_mod = None
				self.cur_inst = None
			elif len(self.stack) == 2:  # 回到模块层
				self.cur_inst = None
		if indent > self.stack[-1]:
			self.stack.append(indent)


def parse(lines) -> AST:
	ast = AST()
	indent_state = IndentState()
	
	for index, line, indent in lines:
		indent_state.update(indent)
		
		# 解析语法
		words = line.split()
		first = words[0]
		others = " ".join(words[1:])
		
		if first == "module":
			match = re.match(r'([a-zA-Z_]\w*)\[(\d+)]:', others)
			if not match:
				line_error("模块定义格式错误", index, line)
			new_mod = AST.Module(match.group(1), int(match.group(2)))
			ast.modules.append(new_mod)
			indent_state.cur_mod = new_mod
			indent_state.cur_inst = None
		
		elif indent_state.cur_mod is not None and first == "input":
			matches = re.findall(r'(\w+)\[(\d+)]', others)
			if not matches:
				line_error("输入端口格式错误", index, line)
			indent_state.cur_mod.inputs.extend([indent_state.cur_mod.Input(name, int(width)) for name, width in matches])
		
		elif indent_state.cur_mod is not None and first == "output":
			output_re = re.compile(r'(\w+)\[(\d+)]\s*<-\s*([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)?)(?:\[(\d+)(?::(\d+))?])?')
			matches = output_re.findall(others)
			if not matches:
				line_error("输出端口格式错误", index, line)
			
			for name, width, source, high_str, low_str in matches:
				slice_info = None
				if high_str:
					high = int(high_str)
					low = int(low_str) if low_str else high
					slice_info = (high, low)
				indent_state.cur_mod.outputs.append(
					indent_state.cur_mod.Output(name, int(width), source, slice_info)
				)
		
		elif indent_state.cur_mod is not None:
			# 尝试匹配子模块例化
			match = re.match(r'([a-zA-Z_]\w*)\s+([a-zA-Z_]\w*)\[(\d+)]:', line)
			if match:
				mod_name = match.group(1)
				inst_name = match.group(2)
				width = int(match.group(3))
				ins = AST.Instance(inst_name, width)
				ins.mod_name = mod_name
				indent_state.cur_mod.instances.append(ins)
				indent_state.cur_inst = ins
			else:
				# 端口映射: port=signal
				eq_pos = line.find("=")
				if eq_pos == -1:
					line_error("端口映射格式错误", index, line)
				port_name = line[:eq_pos].strip()
				signal = line[eq_pos + 1:].strip()
				
				if signal.count("=") > 0:
					line_error("端口映射值应只包含 1 个等号", index, line)
				if not indent_state.cur_inst:
					line_error("端口映射必须在例化语句之后", index, line)
				
				# 检查重复端口
				if any(p == port_name for p, _, _ in indent_state.cur_inst.port_map):
					line_error(f"端口 {port_name} 重复定义", index, line)
				
				# 判断是否是立即数（数字字面量）
				try:
					int(signal, 0)
					# 是立即数，直接存入，不带切片信息
					indent_state.cur_inst.port_map.append((port_name, signal, None))
				except ValueError:
					# 不是立即数，按信号名+切片解析
					signal_re = re.compile(r'^([a-zA-Z_]\w*(?:\.[a-zA-Z_]\w*)?)(?:\[(\d+)(?::(\d+))?])?$')
					match = signal_re.match(signal)
					if not match:
						line_error("信号格式错误", index, line)
					
					base_signal = match.group(1)
					high_str = match.group(2)
					low_str = match.group(3)
					
					slice_info = None
					if high_str is not None:
						high = int(high_str)
						low = int(low_str) if low_str is not None else high
						slice_info = (high, low)
					
					indent_state.cur_inst.port_map.append((port_name, base_signal, slice_info))
				
		else:
			line_error("非法代码", index, line)
		
	# 检查每个模块是否定义了 input 和 output
	for mod in ast.modules:
		if not mod.inputs:
			value_error(f"模块缺少 input 声明", mod.name)
		if not mod.outputs:
			value_error(f"模块缺少 output 声明", mod.name)
	
	return ast

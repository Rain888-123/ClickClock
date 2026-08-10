# src/clickclock/parser.py


import re
from .errors import line_error


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
			def __init__(self, name, width, source) -> None:
				super().__init__(name, width)
				self.source = source
		
		
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
		self.uses = []


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
		
		elif first == "use":
			if indent != 0:
				line_error("use 应该只在顶层出现", index, line)
			items = [item.strip() for item in others.split(",") if item.strip()]
			for item in items:
				if item not in ast.uses:
					ast.uses.append(item)
		
		elif indent_state.cur_mod is not None and first == "input":
			matches = re.findall(r'(\w+)\[(\d+)]', others)
			if not matches:
				line_error("输入端口格式错误", index, line)
			indent_state.cur_mod.inputs.extend([indent_state.cur_mod.Input(name, int(width)) for name, width in matches])
		
		elif indent_state.cur_mod is not None and first == "output":
			matches = re.findall(r'(\w+)\[(\d+)]\s*<-\s*([\w\[\].]+)', others)
			if not matches:
				line_error("输出端口格式错误", index, line)
			indent_state.cur_mod.outputs.extend([indent_state.cur_mod.Output(name, int(width), source) for name, width, source in matches])
		
		elif indent_state.cur_mod is not None and first == "init":
			if indent_state.cur_inst is None:
				line_error("init 必须在例化语句之后", index, line)
			indent_state.cur_inst.init = int(others, 0)
		
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
				
				# 检查等号数量，避免歧义
				if signal.count("=") > 0:
					line_error("端口映射值应只包含 1 个等号", index, line)
				
				if indent_state.cur_inst is None:
					line_error("端口映射必须在例化语句之后", index, line)
				indent_state.cur_inst.port_map.append((port_name, signal))
				
		else:
			line_error("非法代码", index, line)
	
	return ast

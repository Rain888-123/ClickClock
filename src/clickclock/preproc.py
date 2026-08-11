# src/clickclock/preproc.py


from pathlib import Path
from . import loader
from .errors import value_error

def expand(text, base_dir = ".") -> str:
	visited = set()
	result = []
	

	def _process(lines, current_dir) -> None:
		for line in lines:
			stripped = line.strip()
			if not stripped:
				result.append(line)
				continue
			
			words = stripped.split()
			items = [item.strip() for item in " ".join(words[1:]).split(",")]
			if words[0] == "use":
				for name in items:
					if not name:
						value_error("use 后应跟随文件名", str(name))
					filepath = Path(current_dir) / f"{name}.clk"
					abspath = str(filepath.resolve())
					if abspath in visited:
						continue  # 防止循环包含
					visited.add(abspath)
					included = loader.source(name, current_dir)
					sub_lines = included.splitlines(keepends=True)
					_process(sub_lines, str(filepath.parent))
			else:
				result.append(line)

	_process(text.splitlines(keepends=True), base_dir)
	
	return ''.join(result)

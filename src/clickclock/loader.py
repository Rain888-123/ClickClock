# src/clickclock/loader.py


from pathlib import Path

from .errors import file_error


def load_source(name, base_dir = ".") -> str:
	path = Path(base_dir) / f"{name}.clk"
	if not path.exists():
		raise file_error(path)
	
	return path.read_text(encoding="utf-8")


def load_config(name, base_dir = "config") -> dict[str, str|list|bool]:
	path = Path(base_dir) / f"{name}.toml"
	if not path.exists():
		raise file_error(path)
	
	from tomllib import load
	with open(path, "rb") as f:
		return load(f)

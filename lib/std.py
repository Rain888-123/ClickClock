# lib/std.py


def _mask(width) -> int:
	return (1 << width) - 1


def _eval_mux(sel, a, b, width) -> int:
	return (b if sel else a) & _mask(width)


def _eval_dff(we, d, prev, width) -> int:
	return (d if we else prev) & _mask(width)


def _eval_add(a, b, cin, width) -> tuple[int, int]:
	return (a + b + cin) & _mask(width), ((a + b + cin) >> width) & _mask(1)


EVAL_MAP = {
	"mux": _eval_mux,
	"dff": _eval_dff,
	"add": _eval_add,
}

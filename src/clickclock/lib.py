# src/clickclock/lib.py


def _mask(width) -> int:
	return (1 << width) - 1


def _eval_mux(sel, a, b, width) -> int:
	return (b if sel else a) & _mask(width)


def _eval_dff(we, d, prev, width) -> int:
	return (d if we else prev) & _mask(width)


def _eval_add(a, b, cin, width) -> tuple[int, int]:
	return (a + b + cin) & _mask(width), ((a + b + cin) >> width) & _mask(1)


def _eval_not(a, width) -> int:
	return (~a) & _mask(width)


def _eval_and(a, b, width) -> int:
	return (a & b) & _mask(width)


def _eval_xor(a, b, width) -> int:
	return (a ^ b) & _mask(width)


def _eval_or(a, b, width) -> int:
	return (a | b) & _mask(width)


def _eval_nand(a, b, width) -> int:
	return (~(a & b)) & _mask(width)


def _eval_nor(a, b, width) -> int:
	return (~(a | b)) & _mask(width)


def _eval_lsl(a, offset, width) -> int:
	return (a << offset) & _mask(width)


def _eval_lsr(a, offset, width) -> int:
	return (a >> offset) & _mask(width)


def _eval_asr(a, offset, width) -> int:
	shift = 64 - width
	return ((a << shift) >> (offset + shift)) & _mask(width)


EVAL_MAP = {
	"mux": _eval_mux,
	"dff": _eval_dff,
	"add": _eval_add,
	"not": _eval_not,
	"and": _eval_and,
	"xor": _eval_xor,
	"or": _eval_or,
	"nand": _eval_nand,
	"nor": _eval_nor,
	"lsl": _eval_lsl,
	"lsr": _eval_lsr,
	"asr": _eval_asr,
}

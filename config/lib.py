# src/clickclock/lib.py

# Copyright (C) 2026 Rain888
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

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


def _eval_xnor(a, b, width) -> int:
	return ~(a ^ b) & _mask(width)


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


def _eval_eq(a, b, width) -> int:
	return int((a & _mask(width)) == (b & _mask(width))) & _mask(1)


def _eval_ult(a, b, width) -> int:
	return int((a & _mask(width)) < (b & _mask(width))) & _mask(1)


def _eval_slt(a, b, width) -> int:
	sign_a = a >> (width - 1)
	sign_b = b >> (width - 1)
	if sign_a != sign_b:
		return int(sign_a > sign_b)
	else:
		return int((a & _mask(width)) < (b & _mask(width)))


def _eval_dec(in_val, width) -> int:
	idx = in_val & _mask(width)
	return (1 << idx) & _mask(1 << width)


EVAL_MAP = {
	"mux": _eval_mux,
	"dff": _eval_dff,
	"add": _eval_add,
	"not": _eval_not,
	"and": _eval_and,
	"xor": _eval_xor,
	"xnor": _eval_xnor,
	"or": _eval_or,
	"nand": _eval_nand,
	"nor": _eval_nor,
	"lsl": _eval_lsl,
	"lsr": _eval_lsr,
	"asr": _eval_asr,
	"eq": _eval_eq,
	"ult": _eval_ult,
	"slt": _eval_slt,
	"dec": _eval_dec,
}

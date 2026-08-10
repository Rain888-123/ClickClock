# src/clickclock/errors.py


def line_error(msg, index, line) -> None:
    raise SyntaxError(f"{msg}, 第 {index} 行, {line.lstrip()}")


def value_error(msg, something) -> None:
    raise ValueError(f"{msg}，{something}")

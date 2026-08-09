# src/clickclock/errors.py


def error(msg, index, line) -> None:
    raise SyntaxError(f"{msg}, 第 {index} 行, {line.lstrip()}")

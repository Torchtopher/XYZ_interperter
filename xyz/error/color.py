"""
Quick and dirty ANSI colorer for error printing.
"""

from sys import stdout

color: bool = stdout.isatty()
"""Represents a sequence of 2 ANSI style numbers.

Technically requires no specific format,
but use NORMAL or BOLD for the first number
and a color for the second.

These style numbers are constants in this module.
"""
type Styles = tuple[int, int]


def style(styles: Styles, text: str) -> str:
    """Returns a string styled with the provided ANSI style codes."""
    seq: str = ';'.join([str(styles[0]), str(styles[1])])
    return f"\033[{seq}m{text}\033[0m" if color else text


NORMAL = 0
BOLD = 1
BLACK = 30
RED = 31
GREEN = 32
YELLOW = 33
BLUE = 34
MAGENTA = 35
CYAN = 36
WHITE = 37
GRAY = 90

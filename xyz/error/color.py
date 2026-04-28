from sys import stdout

# Quick and dirty ANSI colorer

color: bool = stdout.isatty()
type Styles = tuple[int, int]


def style(styles: Styles, text: str) -> str:
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

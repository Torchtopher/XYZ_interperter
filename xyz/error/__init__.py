from xyz.error.color import (style, NORMAL, BOLD, RED, WHITE, GRAY)
from io import TextIOWrapper

type Span = tuple[int, int]
type LineCol = tuple[int, int]
type LineSpan = tuple[LineCol, LineCol]


class Error:
    span: Span
    file: TextIOWrapper
    text: str

    def __init__(self, span, file):
        self.span = span
        self.file = file

    def message(self) -> str:
        return "No error message"

    def get_text(self):
        original_pos: int = self.file.tell()
        self.file.seek(0)
        self.text = self.file.read()
        self.file.seek(original_pos)

    def get_line_span(self) -> LineSpan:
        original_pos: int = self.file.tell()
        self.file.seek(0)
        txt = self.file.read()
        first: list[str] = txt[:self.span[0]+1].splitlines(keepends=True)
        last: list[str] = txt[:self.span[1]].splitlines(keepends=True)
        span: LineSpan = (
            (len(first), len(first[-1])-1), (len(last), len(last[-1])-1))
        self.file.seek(original_pos)
        return span

    def print(self):
        self.get_text()
        line_span: LineSpan = self.get_line_span()
        print(style((BOLD, WHITE), "XYZ"), style(
            (BOLD, RED), type(self).__name__), "@", "[%s:%s]" % line_span[0])
        print(self.message())
        print()
        lines: list[str] = self.text.splitlines()
        for i in range(line_span[0][0]-1, line_span[1][0]):
            line: str = lines[i]
            start: int = line_span[0][1]-1 if i == line_span[0][0]-1 else 0
            end: int = line_span[1][1] if i == line_span[1][0]-1 else len(line)
            printed: str = ""
            under: str = ""
            for c in range(len(line)):
                is_error: bool = c in range(start, end)
                printed += style((BOLD if is_error else NORMAL,
                                 RED if is_error else WHITE), line[c])
                under += style((BOLD, RED), "~") if is_error else (
                    line[c] if line[c].isspace() else " ")
            print(style((NORMAL, GRAY), str(i)), printed)
            print(" "*len(str(i)), under)
        print("-"*32)

from xyz.error.color import (style, NORMAL, BOLD, RED, WHITE, GRAY)
from io import StringIO

type LineCol = tuple[int, int]
type Span = tuple[LineCol, LineCol]

# An error in the XYZ pipeline.
# Should primarily be handled as values, but can be thrown as exceptions if automatic propagation is needed.

class Error(Exception):
    span: Span
    file: StringIO
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

    def print(self):
        self.get_text()
        print(style((BOLD, WHITE), "XYZ"), style(
            (BOLD, RED), type(self).__name__), "@", "[%s:%s]" % self.span[0])
        print(self.message())
        print()
        lines: list[str] = self.text.splitlines()
        for i in range(self.span[0][0]-1, min(len(lines), self.span[1][0])):
            line: str = lines[i]
            start: int = self.span[0][1]-1 if i == self.span[0][0]-1 else 0
            end: int = self.span[1][1]-1 if i == self.span[1][0]-1 else len(line)
            printed: str = ""
            under: str = ""
            for c in range(len(line)):
                is_error: bool = c in range(start, end)
                printed += style((BOLD if is_error else NORMAL,
                                 RED if is_error else WHITE), line[c])
                under += style((BOLD, RED), "~") if is_error else (
                    line[c] if line[c].isspace() else " ")
            print(style((NORMAL, GRAY), str(i+1)), printed)
            print(" "*len(str(i+1)), under)
        if self.span[1][0] > len(lines):
            print(style((NORMAL, RED), "<EOF>"))
        print("-"*32)

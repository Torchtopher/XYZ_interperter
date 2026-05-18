"""
Type definitions for error reporting.
"""

from xyz.error.color import (style, NORMAL, BOLD, RED, WHITE, GRAY)
from io import StringIO
from sys import stderr

"""A position in a file in the form (line, column), for error reporting."""
type LineCol = tuple[int, int]
"""A span between two positions in a file, for error reporting."""
type Span = tuple[LineCol, LineCol]

class Error(Exception):
    """An error in the XYZ pipeline.

    Should primarily be handled as values to be printed if returned,
    but can be thrown as exceptions if automatic propagation is needed.
    Errors-as-exceptions should always be caught before the end of a step in the pipeline.

    Attributes:
      span:
        The span of code causing the error.
      file:
        The file in which the error occurred, as a StringIO.
        Used to print the erroring code.
    """
    span: Span
    file: StringIO
    __text: str

    def __init__(self, span, file):
        """Initializes the error with a span and file."""
        self.span = span
        self.file = file

    def message(self) -> str:
        """Abstract method returning a message for the error."""
        return "No error message"

    def __get_text(self):
        original_pos: int = self.file.tell()
        self.file.seek(0)
        self.__text = self.file.read()
        self.file.seek(original_pos)

    def print(self):
        """Prints the error to stderr, formatted like this:

        XYZ ErrorSubclass @ [1:1]
        Error message

        1 erroring_code()
          ~~~~~~~~~~~~~~~
        --------------------------------
        """
        self.__get_text()
        print(style((BOLD, WHITE), "XYZ"), style(
            (BOLD, RED), type(self).__name__), "@", "[%s:%s]" % self.span[0], file=stderr)
        print(self.message(), file=stderr)
        print(file=stderr)
        lines: list[str] = self.__text.splitlines()
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
            print(style((NORMAL, GRAY), str(i+1)), printed, file=stderr)
            print(" "*len(str(i+1)), under, file=stderr)
        if self.span[1][0] > len(lines):
            print(style((NORMAL, RED), "<EOF>"), file=stderr)
        print("-"*32, file=stderr)

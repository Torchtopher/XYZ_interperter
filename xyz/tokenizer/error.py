"""
Error definitions for the tokenizer.
"""

from xyz.error import Error


class InvalidTokenError(Error):
    """
    An error returned when a character is encountered that is not a valid token.

    Attributes:
      char: The invalid character.
    """

    char: str

    def __init__(self, span, file, char):
        self.char = char
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Invalid token %s" % self.char


class InvalidEscapeError(Error):
    """
    An error returned when a string contains an escape sequence that is not recognized.

    Attributes:
      char: The invalid start of the escape sequence. (i.e. x for the unimplemented \\x)
    """
    char: str

    def __init__(self, span, file, char):
        self.char = char
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Invalid escape sequence \\%s" % self.char


class StringNewlineError(Error):
    """
    An error returned when a string contains a newline not escaped with a \\.
    """
    def message(self) -> str:
        return "Strings cannot contain unescaped newlines"


class UnexpectedEndError(Error):
    """
    An error returned when the tokenizer reaches the end of a file unexpectedly (i.e. while still reading a string)
    """
    def message(self) -> str:
        return "Unexpected end of file (did you forget to close a string?)"

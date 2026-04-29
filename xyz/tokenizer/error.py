from xyz.error import Error


class InvalidTokenError(Error):
    char: str

    def __init__(self, span, file, char):
        self.char = char
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Invalid token %s" % self.char


class InvalidEscapeError(Error):
    char: str

    def __init__(self, span, file, char):
        self.char = char
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Invalid escape sequence \\%s" % self.char


class StringNewlineError(Error):
    def message(self) -> str:
        return "Strings cannot contain unescaped newlines"


class UnexpectedEndError(Error):
    def message(self) -> str:
        return "Unexpected end of file (did you forget to close a string?)"

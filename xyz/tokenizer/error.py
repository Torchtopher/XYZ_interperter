from xyz.error import Error


class InvalidTokenError(Error):
    char: str

    def __init__(self, span, file, char):
        self.char = char
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Invalid token %s" % self.char

from xyz.error import Error
from xyz.tokenizer.tokens import TokenType

class WrongTokenError(Error):
    expected: TokenType
    def __init__(self, span, file, expected):
        self.expected = expected
        Error.__init__(self, span, file)

    def message(self):
        return "Expected token %s, got:" % self.expected.name

class NoGrammarMatchError(Error):
    expected: str
    def __init__(self, span, file, expected):
        self.expected = expected
        Error.__init__(self, span, file)

    def message(self):
        return "Expected %s, got:" % self.expected

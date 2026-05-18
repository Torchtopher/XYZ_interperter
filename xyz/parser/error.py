"""
Error definitions for the parser.
"""

from xyz.error import Error
from xyz.tokenizer.tokens import TokenType

class WrongTokenError(Error):
    """
    An error returned when a token was expected by the grammar but not found.

    For example, "then" must always appear after the condition in an if statement,
    and if something else appears instead, this error will be returned.

    Attributes:
      expected:
        A list of possible token types that were expected.
    """
    expected: list[TokenType]
    def __init__(self, span, file, expected):
        self.expected = expected
        Error.__init__(self, span, file)

    def message(self):
        return "Expected token %s, got:" % " or ".join([i.name for i in self.expected])

class NoGrammarMatchError(Error):
    """
    An error returned when a piece of code does not match any possibilities for a grammar symbol.

    Attributes:
      expected:
        A description of what was expected (e.x. statement, expression)
    """
    expected: str
    def __init__(self, span, file, expected):
        self.expected = expected
        Error.__init__(self, span, file)

    def message(self):
        return "Expected %s, got:" % self.expected

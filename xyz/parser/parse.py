from io import TextIOWrapper
from typing import Iterator
from xyz.tokenizer import Token, TokenType
import xyz.parser.ast as AST
from xyz.error import Error
from xyz.parser.error import WrongTokenError

# For simplicity, the parser uses the python Exception system instead of an error-as-value system.
# These are converted back to errors-as-values at the top of the parser call stack.

def parse(source: TextIOWrapper, tokens: Iterator[Token]) -> AST.File | Error:
    def expect(type: TokenType) -> Token | WrongTokenError:
        token: Token = next(tokens)
        if not token[0] == type:
            raise WrongTokenError(token[1], source, type)
        else:
            return token

    # ---

    def parse_expression(tokens: Iterator[Token]) -> AST.Expression:
        return None

    try:
        file: AST.File = parse_expression(tokens)
        expect(TokenType.EOF)
    except Error as error: return error
    return file

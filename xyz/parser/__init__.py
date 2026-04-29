from io import TextIOWrapper
from typing import Iterator
from xyz.tokenizer.tokens import Token, TokenType
import xyz.parser.grammar as grammar
from xyz.error import Error
from xyz.parser.error import WrongTokenError

def parse(source: TextIOWrapper, tokens: Iterator[Token]) -> grammar.File | Error:
    def expect(type: TokenType) -> Token | WrongTokenError:
        token: Token = next(tokens)
        if not token[0] == type:
            return WrongTokenError(token[1], source, type)
        else:
            return token

    file: grammar.File = grammar.File(parse_expression(tokens))
    eof: Token | WrongTokenError = expect(TokenType.EOF)
    if isinstance(eof, WrongTokenError):
        return eof
    else:
        return file

def parse_expression(tokens: Iterator[Token]) -> grammar.Expression:
    return None

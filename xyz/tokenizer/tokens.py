from enum import Enum


class TokenType(Enum):
    EOF = 0
    IDENT = 1


type Span = tuple[int, int]
type Token = tuple[TokenType, Span, str | None]

from enum import Enum


class TokenType(Enum):
    EOF = 0
    IDENT = 1
    INT = 2
    FLOAT = 3
    STRING = 4
    SEMICOLON = 5  # ;
    COMMA = 6  # ,
    SET = 7  # =
    DOT = 8  # .
    COLON = 9  # :
    ELLIPSIS = 10  # ...
    PAREN_OPEN = 11  # (
    PAREN_CLOSE = 12  # )
    BRACKET_OPEN = 13  # [
    BRACKET_CLOSE = 14  # ]
    BRACE_OPEN = 15  # {
    BRACE_CLOSE = 16  # }
    KEYWORD_AND = 17
    KEYWORD_BREAK = 18
    KEYWORD_CONST = 19
    KEYWORD_DO = 20
    KEYWORD_ELSE = 21
    KEYWORD_ELSEIF = 22
    KEYWORD_END = 23
    KEYWORD_FALSE = 24
    KEYWORD_FOR = 25
    KEYWORD_FUNCTION = 26
    KEYWORD_IF = 27
    KEYWORD_IN = 28
    KEYWORD_LET = 29
    KEYWORD_NIL = 30
    KEYWORD_NOT = 31
    KEYWORD_OR = 32
    KEYWORD_REPEAT = 33
    KEYWORD_RETURN = 34
    KEYWORD_THEN = 35
    KEYWORD_TRUE = 36
    KEYWORD_UNTIL = 37
    KEYWORD_WHILE = 38
    OP_PLUS = 39  # +
    OP_MINUS = 40  # -
    OP_MUL = 41  # *
    OP_DIV = 42  # /
    OP_FLOORDIV = 43  # //
    OP_EXP = 44  # **
    OP_MOD = 45  # %
    OP_AND = 46  # &
    OP_XOR = 47  # ^
    OP_OR = 48  # |
    OP_RSHIFT = 49  # >>
    OP_LSHIFT = 50  # <<
    OP_CONCAT = 51  # ..
    OP_LESS = 52  # <
    OP_LEQ = 53  # <=
    OP_GREATER = 54  # >
    OP_GEQ = 55  # >=
    OP_EQUAL = 56  # ==
    OP_NEQ = 57  # !=
    OP_SIZE = 58  # #
    OP_NOT = 59  # !


type Span = tuple[int, int]
type Token = tuple[TokenType, Span, str | None]

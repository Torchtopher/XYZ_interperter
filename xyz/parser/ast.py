from typing import Literal
from enum import Enum
from typing import NamedTuple

class BinExpType(Enum):
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    FLOORDIV = 4
    EXP = 5
    MOD = 6
    BIT_AND = 7
    BIT_XOR = 8
    BIT_OR = 9
    LSHIFT = 10
    RSHIFT = 11
    CONCAT = 12
    LESS = 13
    LEQ = 14
    GREATER = 15
    GEQ = 16
    EQUAL = 17
    NEQ = 18
    AND = 19
    OR = 20

class UnExpType(Enum):
    NOT = 0
    NEG = 1
    SIZE = 2


# The rules in this file are NOT for the language grammar, but for the AST.

type File = Expression
type Expression = (LitNil | LitTrue | LitFalse | LitInt | LitFloat | 
                   LitString | LitTable | BinaryExpression | UnaryExpression | VarExpr) # | FunctionCall | Lambda
class LitInt(NamedTuple):
    value: int
class LitFloat(NamedTuple):
    value: float

class LitString(NamedTuple):
    value: str

class LitNil(NamedTuple):
    value: Literal[None]

class LitTrue(NamedTuple):
    value: Literal[True]

class LitFalse(NamedTuple):
    value: Literal[False]

class LitTable(NamedTuple):
    value: list[tuple[Expression, Expression]]
class BinaryExpression(NamedTuple):
    type: BinExpType
    left: Expression
    right: Expression

class UnaryExpression(NamedTuple):
    type: UnExpType
    right: Expression

class VarExpr(NamedTuple):
    name: str
    # no value because can't know what it will be

class GroupedExpr(NamedTuple):
    value: Expression
    # no value because can't know what it will be
from typing import Literal
from enum import Enum

# The rules in this file are NOT for the language grammar, but for the AST.

type File = Expression
type Expression = (LitNil | LitTrue | LitFalse | LitInt | LitFloat | 
                   LitString | LitTable | BinaryExpression | UnaryExpression | Var) # | FunctionCall | Lambda
type LitNil = Literal[None]
type LitTrue = Literal[True]
type LitFalse = Literal[False]
type LitInt = int
type LitFloat = float
type LitString = str
type LitTable = list[tuple[Expression, Expression]]
type BinaryExpression = tuple[BinExpType, Expression, Expression]
type UnaryExpression = tuple[UnExpType, Expression]
type Var = tuple[str]

class BinExpType(Enum):
    INDEX = 0
    ADD = 1
    SUB = 2
    MUL = 3
    DIV = 4
    FLOORDIV = 5
    EXP = 6
    MOD = 7
    BIT_AND = 8
    BIT_XOR = 9
    BIT_OR = 10
    LSHIFT = 11
    RSHIFT = 12
    CONCAT = 13
    LESS = 14
    LEQ = 15
    GREATER = 16
    GEQ = 17
    EQUAL = 18
    NEQ = 19
    AND = 20
    OR = 21

class UnExpType(Enum):
    NOT = 0
    NEG = 1
    SIZE = 2

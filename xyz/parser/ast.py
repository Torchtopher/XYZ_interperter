from typing import Literal
from enum import Enum

# The rules in this file are NOT for the language grammar, but for the AST.

type File = Expression
type Expression = (LitNil | LitTrue | LitFalse | LitInt | LitFloat | 
                   LitString | LitTable | BinaryExpression | UnaryExpression | VarExpr) # | FunctionCall | Lambda
type LitNil = Literal[None] # You have to write this as None instead of LitNil for some reason
type LitTrue = Literal[True] # same
type LitFalse = Literal[False] # same
type LitInt = int
type LitFloat = float
type LitString = str
type LitTable = list[tuple[Expression, Expression]]
type BinaryExpression = tuple[BinExpType, Expression, Expression]
type UnaryExpression = tuple[UnExpType, Expression]
type VarExpr = tuple[str, list[Expression]]

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

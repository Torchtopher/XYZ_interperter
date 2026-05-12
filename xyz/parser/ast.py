from typing import Literal
from enum import Enum
from typing import NamedTuple
from xyz.error import Span

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

type Expression = (LitNil | LitTrue | LitFalse | LitInt | LitFloat | 
                   LitString | LitTable | BinaryExpression | UnaryExpression | Var | Access | FunctionCall | Lambda)
class LitInt(NamedTuple):
    span: Span
    value: int
class LitFloat(NamedTuple):
    span: Span
    value: float

class LitString(NamedTuple):
    span: Span
    value: str

class LitNil(NamedTuple):
    span: Span
    value: Literal[None]

class LitTrue(NamedTuple):
    span: Span
    value: Literal[True]

class LitFalse(NamedTuple):
    span: Span
    value: Literal[False]

class LitTable(NamedTuple):
    span: Span
    value: list[tuple[Expression, Expression]]
class BinaryExpression(NamedTuple):
    span: Span
    type: BinExpType
    left: Expression
    right: Expression

class UnaryExpression(NamedTuple):
    span: Span
    type: UnExpType
    right: Expression

class Var(NamedTuple):
    span: Span
    name: str

class Access(NamedTuple):
    span: Span
    source: Expression
    index: Expression | None

class GroupedExpr(NamedTuple):
    span: Span
    value: Expression

type File = Block
type Statement = (Definition | SetStatement | FunctionCall | Break | Block | WhileLoop | RepeatLoop | IfStatement | ForLoop )
type ReturnStatement = Expression | None

class Block(NamedTuple):
    span: Span
    statements: list[Statement]
    return_statement: ReturnStatement # assumed this return statement is none for things for loops

class Lambda(NamedTuple):
    span: Span
    parameters: list[str]
    extra: str | None
    block: Block

# function definitions are const Definitions if their name is just a variable name
# otherwise they are SetStatements
class Definition(NamedTuple):
    span: Span
    const: bool
    var: list[Var]
    value: list[Expression]

class SetStatement(NamedTuple):
    span: Span
    var: list[Access]
    value: list[Expression]

class FunctionCall(NamedTuple):
    span: Span
    method: bool # whether the function is called with `:` instead of `.` to pass the containing table as the first argument
    source: Expression
    args: list[Expression]

class Break(NamedTuple):
    span: Span
    pass

class WhileLoop(NamedTuple):
    span: Span
    condition: Expression
    block: Block

class RepeatLoop(NamedTuple):
    span: Span
    condition: Expression
    block: Block

class IfStatement(NamedTuple):
    span: Span
    conditions: list[tuple[Expression, Block]]
    else_block: Block | None

class ForLoop(NamedTuple):
    span: Span
    var: str
    start: Expression
    end: Expression
    step: Expression
    block: Block

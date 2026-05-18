from typing import Literal
from enum import Enum
from typing import NamedTuple
from xyz.error import Span

"""
The definition of the XYZ abstract syntax tree.

File is the root node.
All AST nodes have an attribute "span" representing their span in the file for error reporting.
"""

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
    """
    Represents access of a variable or table element for setting, calling, etc.
    
    Attributes:
      source:
        The value to be indexed. Can be any expression, but only a table is valid.
      index:
        The key of the table for which to return the value.
        Can be None, in which case the source itself should be passed through
        (This is used for setting directly to variables, since an Access node is needed for assignment.)
    """
    span: Span
    source: Expression
    index: Expression | None

type File = Block
type Statement = (Definition | SetStatement | FunctionCall | Break | Block | WhileLoop | RepeatLoop | IfStatement | ForLoop )

"""
The return statement of a block.

There is a difference between None and LitNil!
If a ReturnStatement is None, it means the block did not return anything.
If it is LitNil, the block returned nil, so the function should return early if this is a conditional/loop.
"""
type ReturnStatement = Expression | None

class Block(NamedTuple):
    span: Span
    statements: list[Statement]
    return_statement: ReturnStatement

class Lambda(NamedTuple):
    """
    Represents a function.

    There is no statement for the syntax "function name(pars) ; end".
    It is syntactic sugar for "const name = function(pars) ; end", and will therefore be a Definition of a Lambda.
    Similarly, the syntax "function name.name(pars) ; end"
    is syntactic sugar for "name.name = function(pars) ; end", and will be a SetStatement with a Lambda.
    The syntax "function name:name(pars) ; end"
    is syntactic sugar for "name.name = function(self, pars) ; end".

    Attributes:
      parameters:
        A list of parameter names for the function.
        Will be set to corresponding passed arguments in the function scope when called.
      extra:
        The optional name of an "extra" table where passed arguments that do not correspond to parameters will go.
      block:
        The function body.
    """
    span: Span
    parameters: list[str]
    extra: str | None
    block: Block

class Definition(NamedTuple):
    """
    Represents the definition of one or more variables.

    Attributes:
      const:
        Whether the definition was declared with "const", making the variable constant.
      var:
        A list of variable names to define.
      value:
        A list of corresponding values to set.
        Should be the same length as var.
    """
    span: Span
    const: bool
    var: list[Var]
    value: list[Expression]

class SetStatement(NamedTuple):
    """
    Represents the assignment of a value to a variable or table element.

    Attributes:
      var:
        A list of accessors (variables or table elements) to assign to.
      value:
        A list of corresponding values to set.
        Should be the same length as var.
    """
    span: Span
    var: list[Access]
    value: list[Expression]

class FunctionCall(NamedTuple):
    """
    Represents a call to a function.

    Attributes:
      method:
        Whether the function was called with ":" instead of ".".
        The containing table will be passed as the first argument to the function.
      source:
        An expression to call. Only a function is valid.
      args:
        A list of arguments to pass to the function.
        Arguments past the number of parameters will be ignored or put into the "extra" table.
        Arguments not passed will default to nil.
    """
    span: Span
    method: bool
    source: Expression
    args: list[Expression]

class Break(NamedTuple):
    span: Span

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
    """
    Represents a for loop.

    When evaluated, the local variable will be set to start,
    then after each loop be incremented by step
    until it is at least end.

    Attributes:
      var:
        The name of the local variable to use for the loop.
      start:
        The starting value of var. Only a number is valid.
      end:
        The ending value of var. Only a number is valid.
      step:
        The increment of var. Only a number is valid.
      block:
        The loop body.
    """
    span: Span
    var: str
    start: Expression
    end: Expression
    step: Expression
    block: Block

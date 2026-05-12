import pytest

from xyz.eval import debug, BuildStep
from xyz.parser import AST
from xyz.error import Span

def var(span: Span, name: str):
    return AST.Var(span, name)


def integer(span: Span, value: int):
    return AST.LitInt(span, value)


def float_num(span: Span, value: float):
    return AST.LitFloat(span, value)


def unary(span: Span, operator: AST.UnExpType, right: AST.Expression):
    return AST.UnaryExpression(span, operator, right)


def binary(span: Span, operator: AST.BinExpType, left: AST.Expression, right: AST.Expression):
    return AST.BinaryExpression(span, operator, left, right)

def span(s, e) -> Span:
    return ((1,s+7),(1,e+7))


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("a", var(span(1,2), "a")),
        ("_abc123", var(span(1,8), "_abc123")),
        ("1", integer(span(1,2), 1)),
        ("12.34", float_num(span(1,6), 12.34)),
        ("true", AST.LitTrue(span(1,5), True)),
        ("false", AST.LitFalse(span(1,6), False)),
        ("nil", AST.LitNil(span(1,4), None)),
        ("(a)", var(span(2,3), "a")),
    ],
)
def test_primary_expressions(program, expected):
    assert debug("return "+program, BuildStep.PARSE).return_statement == expected


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("!a", unary(span(1,3), AST.UnExpType.NOT, var(span(2,3), "a"))),
        ("not a", unary(span(1,6), AST.UnExpType.NOT, var(span(5,6), "a"))),
        ("-a", unary(span(1,3), AST.UnExpType.NEG, var(span(2,3), "a"))),
        ("#a", unary(span(1,3), AST.UnExpType.SIZE, var(span(2,3), "a"))),
        ("!!a", unary(span(1,4), AST.UnExpType.NOT, unary(span(2,4), AST.UnExpType.NOT, var(span(3,4), "a")))),
        ("!-a", unary(span(1,4), AST.UnExpType.NOT, unary(span(2,4), AST.UnExpType.NEG, var(span(3,4), "a")))),
        ("-#a", unary(span(1,4), AST.UnExpType.NEG, unary(span(2,4), AST.UnExpType.SIZE, var(span(3,4), "a")))),
        ("not !a", unary(span(1,7), AST.UnExpType.NOT, unary(span(5,7), AST.UnExpType.NOT, var(span(6,7), "a")))),
        ("-(a + b)", unary(span(1,9), AST.UnExpType.NEG, binary(span(3,8), AST.BinExpType.ADD, var(span(3,4), "a"), var(span(7,8), "b")))),
    ],
)
def test_unary_expressions(program, expected):
    assert debug("return "+program, BuildStep.PARSE).return_statement == expected


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("a + b", binary(span(1,6), AST.BinExpType.ADD, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a - b", binary(span(1,6), AST.BinExpType.SUB, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a * b", binary(span(1,6), AST.BinExpType.MUL, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a / b", binary(span(1,6), AST.BinExpType.DIV, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a // b", binary(span(1,7), AST.BinExpType.FLOORDIV, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a % b", binary(span(1,6), AST.BinExpType.MOD, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a ** b", binary(span(1,7), AST.BinExpType.EXP, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a & b", binary(span(1,6), AST.BinExpType.BIT_AND, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a ^ b", binary(span(1,6), AST.BinExpType.BIT_XOR, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a | b", binary(span(1,6), AST.BinExpType.BIT_OR, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a >> b", binary(span(1,7), AST.BinExpType.RSHIFT, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a << b", binary(span(1,7), AST.BinExpType.LSHIFT, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a .. b", binary(span(1,7), AST.BinExpType.CONCAT, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a < b", binary(span(1,6), AST.BinExpType.LESS, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a <= b", binary(span(1,7), AST.BinExpType.LEQ, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a > b", binary(span(1,6), AST.BinExpType.GREATER, var(span(1,2), "a"), var(span(5,6), "b"))),
        ("a >= b", binary(span(1,7), AST.BinExpType.GEQ, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a == b", binary(span(1,7), AST.BinExpType.EQUAL, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a != b", binary(span(1,7), AST.BinExpType.NEQ, var(span(1,2), "a"), var(span(6,7), "b"))),
        ("a and b", binary(span(1,8), AST.BinExpType.AND, var(span(1,2), "a"), var(span(7,8), "b"))),
        ("a or b", binary(span(1,7), AST.BinExpType.OR, var(span(1,2), "a"), var(span(6,7), "b"))),
    ],
)
def test_binary_operators(program, expected):
    assert debug("return "+program, BuildStep.PARSE).return_statement == expected


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        (
            "a + b - c",
            AST.BinaryExpression(
                span=((1, 8), (1, 17)),
                type=AST.BinExpType.SUB,
                left=AST.BinaryExpression(
                    span=((1, 8), (1, 13)),
                    type=AST.BinExpType.ADD,
                    left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                    right=AST.Var(span=((1, 12), (1, 13)), name='b')),
                right=AST.Var(span=((1, 16), (1, 17)), name='c'))
        ),
        (
            "a * b / c // d % e",
            AST.BinaryExpression(
                span=((1, 8), (1, 26)),
                type=AST.BinExpType.MOD,
                left=AST.BinaryExpression(
                    span=((1, 8), (1, 22)),
                    type=AST.BinExpType.FLOORDIV,
                    left=AST.BinaryExpression(
                        span=((1, 8), (1, 17)),
                        type=AST.BinExpType.DIV,
                        left=AST.BinaryExpression(
                            span=((1, 8), (1, 13)),
                            type=AST.BinExpType.MUL,
                            left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                            right=AST.Var(span=((1, 12), (1, 13)), name='b')),
                        right=AST.Var(span=((1, 16), (1, 17)), name='c')),
                    right=AST.Var(span=((1, 21), (1, 22)), name='d')),
                right=AST.Var(span=((1, 25), (1, 26)), name='e'))
        ),
        (
            "a < b <= c > d >= e == f != g",
            AST.BinaryExpression(
                span=((1, 8), (1, 37)),
                type=AST.BinExpType.NEQ,
                left=AST.BinaryExpression(
                    span=((1, 8), (1, 32)),
                    type=AST.BinExpType.EQUAL,
                    left=AST.BinaryExpression(
                        span=((1, 8), (1, 27)),
                        type=AST.BinExpType.GEQ,
                        left=AST.BinaryExpression(
                            span=((1, 8), (1, 22)),
                            type=AST.BinExpType.GREATER,
                            left=AST.BinaryExpression(
                                span=((1, 8), (1, 18)),
                                type=AST.BinExpType.LEQ,
                                left=AST.BinaryExpression(
                                    span=((1, 8), (1, 13)),
                                    type=AST.BinExpType.LESS,
                                    left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                                    right=AST.Var(span=((1, 12), (1, 13)), name='b')),
                                right=AST.Var(span=((1, 17), (1, 18)), name='c')),
                            right=AST.Var(span=((1, 21), (1, 22)), name='d')),
                        right=AST.Var(span=((1, 26), (1, 27)), name='e')),
                    right=AST.Var(span=((1, 31), (1, 32)), name='f')),
                right=AST.Var(span=((1, 36), (1, 37)), name='g'))
        ),
        (
            "a | b ^ c & d",
            AST.BinaryExpression(
                span=((1, 8), (1, 21)),
                type=AST.BinExpType.BIT_OR,
                left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                right=AST.BinaryExpression(
                    span=((1, 12), (1, 21)),
                    type=AST.BinExpType.BIT_XOR,
                    left=AST.Var(span=((1, 12), (1, 13)), name='b'),
                    right=AST.BinaryExpression(
                        span=((1, 16), (1, 21)),
                        type=AST.BinExpType.BIT_AND,
                        left=AST.Var(span=((1, 16), (1, 17)), name='c'),
                        right=AST.Var(span=((1, 20), (1, 21)), name='d'))))
        ),
        (
            "a << b >> c",
            AST.BinaryExpression(
                span=((1, 8), (1, 19)),
                type=AST.BinExpType.RSHIFT,
                left=AST.BinaryExpression(
                    span=((1, 8), (1, 14)),
                    type=AST.BinExpType.LSHIFT,
                    left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                    right=AST.Var(span=((1, 13), (1, 14)), name='b')),
                right=AST.Var(span=((1, 18), (1, 19)), name='c'))
        ),
        (
            "a .. b .. c",
            AST.BinaryExpression(
                span=((1, 8), (1, 19)),
                type=AST.BinExpType.CONCAT,
                left=AST.BinaryExpression(
                    span=((1, 8), (1, 14)),
                    type=AST.BinExpType.CONCAT,
                    left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                    right=AST.Var(span=((1, 13), (1, 14)), name='b')),
                right=AST.Var(span=((1, 18), (1, 19)), name='c'))
        ),
        (
            "-a + #b",
            AST.BinaryExpression(
                span=((1, 8), (1, 15)),
                type=AST.BinExpType.ADD,
                left=AST.UnaryExpression(
                    span=((1, 8), (1, 10)),
                    type=AST.UnExpType.NEG,
                    right=AST.Var(span=((1, 9), (1, 10)), name='a')),
                right=AST.UnaryExpression(
                    span=((1, 13), (1, 15)),
                    type=AST.UnExpType.SIZE,
                    right=AST.Var(span=((1, 14), (1, 15)), name='b')))
        ),
        (
            "(a + b) - c",
            AST.BinaryExpression(
                span=((1, 8), (1, 19)),
                type=AST.BinExpType.SUB,
                left=AST.BinaryExpression(
                    span=((1, 9), (1, 14)),
                    type=AST.BinExpType.ADD,
                    left=AST.Var(span=((1, 9), (1, 10)), name='a'),
                    right=AST.Var(span=((1, 13), (1, 14)), name='b')),
                right=AST.Var(span=((1, 18), (1, 19)), name='c'))
        ),
        (
            "a * (b - c)",
            AST.BinaryExpression(
                span=((1, 8), (1, 19)),
                type=AST.BinExpType.MUL,
                left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                right=AST.BinaryExpression(
                    span=((1, 13), (1, 18)),
                    type=AST.BinExpType.SUB,
                    left=AST.Var(span=((1, 13), (1, 14)), name='b'),
                    right=AST.Var(span=((1, 17), (1, 18)), name='c')))
        ),
        (
            "a or b and c",
            AST.BinaryExpression(
                span=((1, 8), (1, 20)),
                type=AST.BinExpType.OR,
                left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                right=AST.BinaryExpression(
                    span=((1, 13), (1, 20)),
                    type=AST.BinExpType.AND,
                    left=AST.Var(span=((1, 13), (1, 14)), name='b'),
                    right=AST.Var(span=((1, 19), (1, 20)), name='c')))
        ),
        (
            "a and b >= c | d ^ e & f << g .. h + i * j ** k",
            AST.BinaryExpression(
                span=((1, 8), (1, 55)),
                type=AST.BinExpType.AND,
                left=AST.Var(span=((1, 8), (1, 9)), name='a'),
                right=AST.BinaryExpression(
                    span=((1, 14), (1, 55)),
                    type=AST.BinExpType.GEQ, 
                    left=AST.Var(span=((1, 14), (1, 15)), name='b'),
                    right=AST.BinaryExpression(
                        span=((1, 19), (1, 55)),
                        type=AST.BinExpType.BIT_OR,
                        left=AST.Var(span=((1, 19), (1, 20)), name='c'),
                        right=AST.BinaryExpression(
                            span=((1, 23), (1, 55)),
                            type=AST.BinExpType.BIT_XOR,
                            left=AST.Var(span=((1, 23), (1, 24)), name='d'),
                            right=AST.BinaryExpression(
                                span=((1, 27), (1, 55)),
                                type=AST.BinExpType.BIT_AND,
                                left=AST.Var(span=((1, 27), (1, 28)), name='e'),
                                right=AST.BinaryExpression(
                                    span=((1, 31), (1, 55)),
                                    type=AST.BinExpType.LSHIFT,
                                    left=AST.Var(span=((1, 31), (1, 32)), name='f'),
                                    right=AST.BinaryExpression(
                                        span=((1, 36), (1, 55)),
                                        type=AST.BinExpType.CONCAT,
                                        left=AST.Var(span=((1, 36), (1, 37)), name='g'),
                                        right=AST.BinaryExpression(
                                            span=((1, 41), (1, 55)),
                                            type=AST.BinExpType.ADD,
                                            left=AST.Var(span=((1, 41), (1, 42)), name='h'),
                                            right=AST.BinaryExpression(
                                                span=((1, 45), (1, 55)),
                                                type=AST.BinExpType.MUL,
                                                left=AST.Var(span=((1, 45), (1, 46)), name='i'),
                                                right=AST.BinaryExpression(
                                                    span=((1, 49), (1, 55)),
                                                    type=AST.BinExpType.EXP,
                                                    left=AST.Var(span=((1, 49), (1, 50)), name='j'),
                                                    right=AST.Var(span=((1, 54), (1, 55)), name='k')))))))))))
        ),
    ],
)
def test_compound_expressions(program, expected):
    assert debug("return "+program, BuildStep.PARSE).return_statement == expected

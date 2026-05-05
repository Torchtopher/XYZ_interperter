import pytest
from pathlib import Path

from main import build_program
from xyz.parser import AST


def var(name: str):
    return AST.VarExpr(name, [])


def integer(value: int):
    return AST.LitInt(value)


def float_num(value: float):
    return AST.LitFloat(value)


def unary(operator: AST.UnExpType, right: AST.Expression):
    return AST.UnaryExpression(operator, right)


def binary(operator: AST.BinExpType, left: AST.Expression, right: AST.Expression):
    return AST.BinaryExpression(operator, left, right)


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("a", var("a")),
        ("_abc123", var("_abc123")),
        ("1", integer(1)),
        ("12.34", float_num(12.34)),
        ("true", AST.LitTrue(True)),
        ("false", AST.LitFalse(False)),
        ("nil", AST.LitNil(None)),
        ("(a)", var("a")),
    ],
)
def test_primary_expressions(program, expected):
    assert build_program(program).return_statement == expected


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("!a", unary(AST.UnExpType.NOT, var("a"))),
        ("not a", unary(AST.UnExpType.NOT, var("a"))),
        ("-a", unary(AST.UnExpType.NEG, var("a"))),
        ("#a", unary(AST.UnExpType.SIZE, var("a"))),
        ("!!a", unary(AST.UnExpType.NOT, unary(AST.UnExpType.NOT, var("a")))),
        ("!-a", unary(AST.UnExpType.NOT, unary(AST.UnExpType.NEG, var("a")))),
        ("-#a", unary(AST.UnExpType.NEG, unary(AST.UnExpType.SIZE, var("a")))),
        ("not !a", unary(AST.UnExpType.NOT, unary(AST.UnExpType.NOT, var("a")))),
        ("-(a + b)", unary(AST.UnExpType.NEG, binary(AST.BinExpType.ADD, var("a"), var("b")))),
    ],
)
def test_unary_expressions(program, expected):
    assert build_program(program).return_statement == expected


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("a + b", binary(AST.BinExpType.ADD, var("a"), var("b"))),
        ("a - b", binary(AST.BinExpType.SUB, var("a"), var("b"))),
        ("a * b", binary(AST.BinExpType.MUL, var("a"), var("b"))),
        ("a / b", binary(AST.BinExpType.DIV, var("a"), var("b"))),
        ("a // b", binary(AST.BinExpType.FLOORDIV, var("a"), var("b"))),
        ("a % b", binary(AST.BinExpType.MOD, var("a"), var("b"))),
        ("a ** b", binary(AST.BinExpType.EXP, var("a"), var("b"))),
        ("a & b", binary(AST.BinExpType.BIT_AND, var("a"), var("b"))),
        ("a ^ b", binary(AST.BinExpType.BIT_XOR, var("a"), var("b"))),
        ("a | b", binary(AST.BinExpType.BIT_OR, var("a"), var("b"))),
        ("a >> b", binary(AST.BinExpType.RSHIFT, var("a"), var("b"))),
        ("a << b", binary(AST.BinExpType.LSHIFT, var("a"), var("b"))),
        ("a .. b", binary(AST.BinExpType.CONCAT, var("a"), var("b"))),
        ("a < b", binary(AST.BinExpType.LESS, var("a"), var("b"))),
        ("a <= b", binary(AST.BinExpType.LEQ, var("a"), var("b"))),
        ("a > b", binary(AST.BinExpType.GREATER, var("a"), var("b"))),
        ("a >= b", binary(AST.BinExpType.GEQ, var("a"), var("b"))),
        ("a == b", binary(AST.BinExpType.EQUAL, var("a"), var("b"))),
        ("a != b", binary(AST.BinExpType.NEQ, var("a"), var("b"))),
        ("a and b", binary(AST.BinExpType.AND, var("a"), var("b"))),
        ("a or b", binary(AST.BinExpType.OR, var("a"), var("b"))),
    ],
)
def test_binary_operators(program, expected):
    assert build_program(program).return_statement == expected


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        (
            "a + b - c",
            binary(
                AST.BinExpType.SUB,
                binary(AST.BinExpType.ADD, var("a"), var("b")),
                var("c"),
            ),
        ),
        (
            "a * b / c // d % e",
            binary(
                AST.BinExpType.MOD,
                binary(
                    AST.BinExpType.FLOORDIV,
                    binary(
                        AST.BinExpType.DIV,
                        binary(AST.BinExpType.MUL, var("a"), var("b")),
                        var("c"),
                    ),
                    var("d"),
                ),
                var("e"),
            ),
        ),
        (
            "a < b <= c > d >= e == f != g",
            binary(
                AST.BinExpType.NEQ,
                binary(
                    AST.BinExpType.EQUAL,
                    binary(
                        AST.BinExpType.GEQ,
                        binary(
                            AST.BinExpType.GREATER,
                            binary(
                                AST.BinExpType.LEQ,
                                binary(AST.BinExpType.LESS, var("a"), var("b")),
                                var("c"),
                            ),
                            var("d"),
                        ),
                        var("e"),
                    ),
                    var("f"),
                ),
                var("g"),
            ),
        ),
        (
            "a | b ^ c & d",
            binary(
                AST.BinExpType.BIT_OR,
                var("a"),
                binary(
                    AST.BinExpType.BIT_XOR,
                    var("b"),
                    binary(AST.BinExpType.BIT_AND, var("c"), var("d")),
                ),
            ),
        ),
        (
            "a << b >> c",
            binary(
                AST.BinExpType.RSHIFT,
                binary(AST.BinExpType.LSHIFT, var("a"), var("b")),
                var("c"),
            ),
        ),
        (
            "a .. b .. c",
            binary(
                AST.BinExpType.CONCAT,
                binary(AST.BinExpType.CONCAT, var("a"), var("b")),
                var("c"),
            ),
        ),
        (
            "-a + #b",
            binary(
                AST.BinExpType.ADD,
                unary(AST.UnExpType.NEG, var("a")),
                unary(AST.UnExpType.SIZE, var("b")),
            ),
        ),
        (
            "(a + b) - c",
            binary(
                AST.BinExpType.SUB,
                binary(AST.BinExpType.ADD, var("a"), var("b")),
                var("c"),
            ),
        ),
        (
            "a * (b - c)",
            binary(
                AST.BinExpType.MUL,
                var("a"),
                binary(AST.BinExpType.SUB, var("b"), var("c")),
            ),
        ),
        (
            "a or b and c",
            binary(
                AST.BinExpType.OR,
                var("a"),
                binary(AST.BinExpType.AND, var("b"), var("c")),
            ),
        ),
        (
            "a and b >= c | d ^ e & f << g .. h + i * j ** k",
            binary(
                AST.BinExpType.AND,
                var("a"),
                binary(
                    AST.BinExpType.GEQ,
                    var("b"),
                    binary(
                        AST.BinExpType.BIT_OR,
                        var("c"),
                        binary(
                            AST.BinExpType.BIT_XOR,
                            var("d"),
                            binary(
                                AST.BinExpType.BIT_AND,
                                var("e"),
                                binary(
                                    AST.BinExpType.LSHIFT,
                                    var("f"),
                                    binary(
                                        AST.BinExpType.CONCAT,
                                        var("g"),
                                        binary(
                                            AST.BinExpType.ADD,
                                            var("h"),
                                            binary(
                                                AST.BinExpType.MUL,
                                                var("i"),
                                                binary(AST.BinExpType.EXP, var("j"), var("k")),
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ],
)
def test_compound_expressions(program, expected):
    assert build_program(program).return_statement == expected

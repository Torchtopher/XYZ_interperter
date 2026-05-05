import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from main import build_program
from xyz.parser import AST


def var(name: str):
    return AST.VarExpr(name)


def integer(value: str):
    return AST.LitInt(value)


def unary(operator: AST.UnExpType, right: AST.Expression):
    return AST.UnaryExpression(operator, right)


def binary(operator: AST.BinExpType, left: AST.Expression, right: AST.Expression):
    return AST.BinaryExpression(operator, left, right)


@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("a", var("a")),
        ("1", integer("1")),
        ("!a", unary(AST.UnExpType.NOT, var("a"))),
        ("-a", unary(AST.UnExpType.NEG, var("a"))),
        ("#a", unary(AST.UnExpType.SIZE, var("a"))),
        ("!!a", unary(AST.UnExpType.NOT, unary(AST.UnExpType.NOT, var("a")))),
        ("!-a", unary(AST.UnExpType.NOT, unary(AST.UnExpType.NEG, var("a")))),
        ("-#a", unary(AST.UnExpType.NEG, unary(AST.UnExpType.SIZE, var("a")))),
        ("a + b", binary(AST.BinExpType.ADD, var("a"), var("b"))),
        ("a - b", binary(AST.BinExpType.SUB, var("a"), var("b"))),
        (
            "a + b - c",
            binary(
                AST.BinExpType.SUB,
                binary(AST.BinExpType.ADD, var("a"), var("b")),
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
                AST.GroupedExpr(binary(AST.BinExpType.ADD, var("a"), var("b"))),
                var("c"),
            ),
        ),
        (
            "a * (b - c)",
            binary(
                AST.BinExpType.MUL,
                var("a"),
                AST.GroupedExpr(binary(AST.BinExpType.SUB, var("b"), var("c"))),
            ),
        ),
    ],
)
def test_supported_expressions(program, expected):
    assert build_program(program) == expected

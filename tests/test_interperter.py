import pytest

import xyz.parser.ast as AST

from xyz.interpreter.interpreter import XYZInterperter


def eval_expr(expr: AST.Expression, global_var_table: dict | None = None):
    interpreter = XYZInterperter(global_var_table)
    return interpreter.eval_expression(expr)


def exec_stmt(statement: AST.Statement, global_var_table: dict | None = None):
    interpreter = XYZInterperter(global_var_table)
    interpreter.exec_statement(statement)
    return interpreter.GVT


def literal(value):
    if value is True:
        return AST.LitTrue(True)
    if value is False:
        return AST.LitFalse(False)
    if value is None:
        return AST.LitNil(None)
    if isinstance(value, int):
        return AST.LitInt(value)
    if isinstance(value, float):
        return AST.LitFloat(value)
    return AST.LitString(value)


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (AST.LitFalse(False), False),
        (AST.LitTrue(True), True),
        (AST.LitNil(None), None),
        (AST.LitInt(12), 12),
        (AST.LitFloat(12.34), 12.34),
        (AST.LitString("hello"), "hello"),
    ],
)
def test_evaluates_literal_expressions(expr, expected):
    assert eval_expr(expr) == expected


def test_evaluates_table_expression():
    expr = AST.LitTable(
        [
            (AST.LitString("name"), AST.LitString("xyz")),
            (AST.LitInt(1), AST.LitTrue(True)),
        ]
    )

    assert eval_expr(expr) == {"name": "xyz", 1: True}


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (AST.UnaryExpression(AST.UnExpType.NOT, AST.LitTrue(True)), False),
        (AST.UnaryExpression(AST.UnExpType.NOT, AST.LitFalse(False)), True),
        (AST.UnaryExpression(AST.UnExpType.NOT, AST.LitNil(None)), True),
        (AST.UnaryExpression(AST.UnExpType.NEG, AST.LitInt(10)), -10),
        (
            AST.UnaryExpression(
                AST.UnExpType.SIZE,
                AST.LitTable([(AST.LitString("key"), AST.LitInt(1))]),
            ),
            1,
        ),
    ],
)
def test_evaluates_unary_expressions(expr, expected):
    assert eval_expr(expr) == expected


@pytest.mark.parametrize(
    ("operator", "left", "right", "expected"),
    [
        (AST.BinExpType.ADD, 7, 3, 10),
        (AST.BinExpType.SUB, 7, 3, 4),
        (AST.BinExpType.MUL, 7, 3, 21),
        (AST.BinExpType.DIV, 7, 2, 3.5),
        (AST.BinExpType.FLOORDIV, 7, 2, 3),
        (AST.BinExpType.EXP, 2, 3, 8),
        (AST.BinExpType.MOD, 7, 3, 1),
        (AST.BinExpType.LESS, 2, 3, True),
        (AST.BinExpType.LEQ, 3, 3, True),
        (AST.BinExpType.GREATER, 3, 2, True),
        (AST.BinExpType.GEQ, 3, 3, True),
        (AST.BinExpType.BIT_AND, 6, 3, 2),
        (AST.BinExpType.BIT_XOR, 6, 3, 5),
        (AST.BinExpType.BIT_OR, 6, 3, 7),
        (AST.BinExpType.LSHIFT, 3, 2, 12),
        (AST.BinExpType.RSHIFT, 8, 1, 4),
        (AST.BinExpType.EQUAL, 3, 3, True),
        (AST.BinExpType.NEQ, 3, 4, True),
        (AST.BinExpType.AND, True, False, False),
        (AST.BinExpType.OR, False, "fallback", "fallback"),
        (AST.BinExpType.CONCAT, "x", 7, "x7"),
    ],
)
def test_evaluates_binary_expressions(operator, left, right, expected):
    expr = AST.BinaryExpression(
        operator,
        literal(left),
        literal(right),
    )

    assert eval_expr(expr) == expected


def test_evaluates_var_expression_from_global_var_table():
    assert eval_expr(AST.Var("answer"), {"answer": 42}) == 42


def test_evaluates_access_expression():
    expr = AST.Access(AST.Var("table_name"), AST.LitString("field"))
    assert eval_expr(expr, {"table_name": {"field": 99}}) == 99


def test_evaluates_nested_access_chain_with_access_as_index():
    # a[f(x).c].b
    expr = AST.Access(
        AST.Access(
            AST.Var("a"),
            AST.Access(
                AST.Var("fx_result"),
                AST.LitString("c"),
            ),
        ),
        AST.LitString("b"),
    )
    global_var_table = {
        "a": {
            "k": {
                "b": 99,
            },
        },
        "fx_result": {
            "c": "k",
        },
    }

    assert eval_expr(expr, global_var_table) == 99


def test_set_statement_creates_top_level_variable():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), None)],
        [AST.LitInt(10)],
    )

    assert exec_stmt(statement) == {"a": 10}


def test_set_statement_replaces_top_level_variable():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), None)],
        [AST.LitInt(20)],
    )

    assert exec_stmt(statement, {"a": 10}) == {"a": 20}


def test_set_statement_evaluates_value_expression_before_assignment():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), None)],
        [
            AST.BinaryExpression(
                AST.BinExpType.ADD,
                AST.LitInt(2),
                AST.LitInt(3),
            )
        ],
    )

    assert exec_stmt(statement) == {"a": 5}


def test_set_statement_assigns_into_existing_table():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), AST.LitString("b"))],
        [AST.LitInt(10)],
    )

    assert exec_stmt(statement, {"a": {}}) == {"a": {"b": 10}}


def test_set_statement_assigns_into_nested_access_target():
    statement = AST.SetStatement(
        [
            AST.Access(
                AST.Access(AST.Var("a"), AST.LitString("b")),
                AST.LitString("c"),
            )
        ],
        [AST.LitInt(10)],
    )

    assert exec_stmt(statement, {"a": {"b": {}}}) == {"a": {"b": {"c": 10}}}


def test_set_statement_assigns_with_access_expression_as_index():
    statement = AST.SetStatement(
        [
            AST.Access(
                AST.Var("a"),
                AST.Access(AST.Var("fx_result"), AST.LitString("c")),
            )
        ],
        [AST.LitInt(10)],
    )
    global_var_table = {
        "a": {"k": 1},
        "fx_result": {"c": "k"},
    }

    assert exec_stmt(statement, global_var_table) == {
        "a": {"k": 10},
        "fx_result": {"c": "k"},
    }


def test_set_statement_assigns_into_nested_target_with_computed_inner_index():
    statement = AST.SetStatement(
        [
            AST.Access(
                AST.Access(
                    AST.Var("a"),
                    AST.Access(AST.Var("fx_result"), AST.LitString("c")),
                ),
                AST.LitString("b"),
            )
        ],
        [AST.LitInt(10)],
    )
    global_var_table = {
        "a": {"k": {"b": 99}},
        "fx_result": {"c": "k"},
    }

    assert exec_stmt(statement, global_var_table) == {
        "a": {"k": {"b": 10}},
        "fx_result": {"c": "k"},
    }


def test_set_statement_assigns_multiple_targets():
    statement = AST.SetStatement(
        [
            AST.Access(AST.Var("a"), None),
            AST.Access(AST.Var("table"), AST.LitString("field")),
        ],
        [
            AST.LitInt(1),
            AST.LitString("value"),
        ],
    )

    assert exec_stmt(statement, {"table": {}}) == {
        "a": 1,
        "table": {"field": "value"},
    }


def test_set_statement_rejects_mismatched_target_and_value_counts():
    statement = AST.SetStatement(
        [
            AST.Access(AST.Var("a"), None),
            AST.Access(AST.Var("b"), None),
        ],
        [AST.LitInt(1)],
    )

    with pytest.raises(RuntimeError, match="same number"):
        exec_stmt(statement)


def test_set_statement_rejects_no_index_target_that_is_not_a_variable():
    statement = AST.SetStatement(
        [AST.Access(AST.LitString("not_a_var"), None)],
        [AST.LitInt(1)],
    )

    with pytest.raises(AssertionError, match="must be a variable"):
        exec_stmt(statement)

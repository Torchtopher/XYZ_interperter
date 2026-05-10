import pytest

import xyz.parser.ast as AST

from xyz.interpreter.interpreter import XYZInterperter
from xyz.interpreter.scoped_env import Scope


def scope(values: dict | None = None) -> Scope:
    env = Scope(None, "test")
    for name, value in (values or {}).items():
        env.define(name, value)
    return env


def scope_values(env: Scope):
    return {name: var.value for name, var in env.table.items()}


def eval_expr(expr: AST.Expression, global_var_table: dict | Scope | None = None):
    env = global_var_table if isinstance(global_var_table, Scope) else scope(global_var_table)
    interpreter = XYZInterperter(env)
    return interpreter.eval_expression(expr)


def exec_stmt(statement: AST.Statement, global_var_table: dict | Scope | None = None):
    env = global_var_table if isinstance(global_var_table, Scope) else scope(global_var_table)
    interpreter = XYZInterperter(env)
    interpreter.exec_statement(statement)
    return interpreter.GVT


def eval_file(ast_file: AST.File, global_var_table: dict | Scope | None = None):
    env = global_var_table if isinstance(global_var_table, Scope) else scope(global_var_table)
    interpreter = XYZInterperter(env)
    for statement in ast_file.statements:
        interpreter.exec_statement(statement)
    return interpreter.eval_expression(ast_file.return_statement), interpreter.GVT


ACCESS_AND_DEFINITION_AST = AST.Block(
    statements=[
        AST.Definition(
            const=False,
            var=[AST.Var("a")],
            value=[
                AST.LitTable(
                    [
                        (
                            AST.LitString("k"),
                            AST.LitTable([(AST.LitString("b"), AST.LitInt(99))]),
                        )
                    ]
                )
            ],
        ),
        AST.Definition(
            const=True,
            var=[AST.Var("fx_result")],
            value=[
                AST.LitTable(
                    [
                        (AST.LitString("c"), AST.LitString("k")),
                    ]
                )
            ],
        ),
        AST.SetStatement(
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
        ),
    ],
    return_statement=AST.Access(
        AST.Access(
            AST.Var("a"),
            AST.Access(AST.Var("fx_result"), AST.LitString("c")),
        ),
        AST.LitString("b"),
    ),
)


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


def test_example_ast_defines_values_sets_nested_access_and_returns_result():
    result, env = eval_file(ACCESS_AND_DEFINITION_AST)

    assert result == 10
    assert scope_values(env) == {
        "a": {"k": {"b": 10}},
        "fx_result": {"c": "k"},
    }


def test_definition_creates_let_variable():
    statement = AST.Definition(
        const=False,
        var=[AST.Var("a")],
        value=[AST.LitInt(10)],
    )

    env = exec_stmt(statement)

    assert env.get("a") == 10
    assert env.resolve_var("a").const is False


def test_definition_creates_const_variable():
    statement = AST.Definition(
        const=True,
        var=[AST.Var("a")],
        value=[AST.LitInt(10)],
    )

    env = exec_stmt(statement)

    assert env.get("a") == 10
    assert env.resolve_var("a").const is True


def test_definition_creates_multiple_variables():
    statement = AST.Definition(
        const=False,
        var=[AST.Var("a"), AST.Var("b")],
        value=[AST.LitInt(1), AST.LitString("two")],
    )

    assert scope_values(exec_stmt(statement)) == {"a": 1, "b": "two"}


def test_set_statement_replaces_existing_variable():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), None)],
        [AST.LitInt(20)],
    )

    assert exec_stmt(statement, {"a": 10}).get("a") == 20


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

    assert exec_stmt(statement, {"a": 0}).get("a") == 5


def test_set_statement_assigns_into_existing_table():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), AST.LitString("b"))],
        [AST.LitInt(10)],
    )

    assert scope_values(exec_stmt(statement, {"a": {}})) == {"a": {"b": 10}}


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

    assert scope_values(exec_stmt(statement, {"a": {"b": {}}})) == {
        "a": {"b": {"c": 10}}
    }


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

    assert scope_values(exec_stmt(statement, global_var_table)) == {
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

    assert scope_values(exec_stmt(statement, global_var_table)) == {
        "a": {"k": {"b": 10}},
        "fx_result": {"c": "k"},
    }


def test_set_statement_assigns_multiple_existing_targets():
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

    assert scope_values(exec_stmt(statement, {"a": 0, "table": {}})) == {
        "a": 1,
        "table": {"field": "value"},
    }


def test_set_statement_rejects_unbound_variable_assignment():
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), None)],
        [AST.LitInt(1)],
    )

    with pytest.raises(RuntimeError, match="unbound variable"):
        exec_stmt(statement)


def test_set_statement_rejects_const_variable_reassignment():
    env = scope()
    env.define("a", 1, const=True)
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), None)],
        [AST.LitInt(2)],
    )

    with pytest.raises(RuntimeError, match="const variable"):
        exec_stmt(statement, env)


def test_set_statement_can_mutate_table_stored_in_const_variable():
    env = scope()
    env.define("a", {"b": 1}, const=True)
    statement = AST.SetStatement(
        [AST.Access(AST.Var("a"), AST.LitString("b"))],
        [AST.LitInt(2)],
    )

    assert scope_values(exec_stmt(statement, env)) == {"a": {"b": 2}}


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


def test_definition_rejects_mismatched_target_and_value_counts():
    statement = AST.Definition(
        const=False,
        var=[AST.Var("a"), AST.Var("b")],
        value=[AST.LitInt(1)],
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


def test_for_loop_updates_outer_variable():
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=False,
                var=[AST.Var("sum")],
                value=[AST.LitInt(0)],
            ),
            AST.ForLoop(
                var="i",
                start=AST.LitInt(1),
                end=AST.LitInt(4),
                step=AST.LitInt(1),
                block=AST.Block(
                    statements=[
                        AST.SetStatement(
                            var=[AST.Access(AST.Var("sum"), None)],
                            value=[
                                AST.BinaryExpression(
                                    AST.BinExpType.ADD,
                                    AST.Var("sum"),
                                    AST.Var("i"),
                                )
                            ],
                        )
                    ],
                    return_statement=AST.LitNil(None),
                ),
            ),
        ],
        return_statement=AST.Var("sum"),
    )

    result, env = eval_file(ast_file)

    assert result == 6
    assert scope_values(env) == {"sum": 6}


def test_for_loop_variable_is_not_visible_after_loop():
    ast_file = AST.Block(
        statements=[
            AST.ForLoop(
                var="i",
                start=AST.LitInt(1),
                end=AST.LitInt(2),
                step=AST.LitInt(1),
                block=AST.Block(
                    statements=[],
                    return_statement=AST.LitNil(None),
                ),
            ),
        ],
        return_statement=AST.Var("i"),
    )

    with pytest.raises(RuntimeError, match="unbound variable"):
        eval_file(ast_file)


def test_for_loop_does_not_run_body_when_range_is_empty():
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=False,
                var=[AST.Var("sum")],
                value=[AST.LitInt(0)],
            ),
            AST.ForLoop(
                var="i",
                start=AST.LitInt(4),
                end=AST.LitInt(1),
                step=AST.LitInt(1),
                block=AST.Block(
                    statements=[
                        AST.SetStatement(
                            var=[AST.Access(AST.Var("sum"), None)],
                            value=[AST.LitInt(99)],
                        )
                    ],
                    return_statement=AST.LitNil(None),
                ),
            ),
        ],
        return_statement=AST.Var("sum"),
    )

    result, env = eval_file(ast_file)

    assert result == 0
    assert scope_values(env) == {"sum": 0}


def test_function_sums_one_to_ten_and_returns_result():
    # const a = function()
    #     let sum = 0
    #     for i = 1, 11, 1 do
    #         set sum = sum + i
    #     end
    #     return sum
    # end
    # return a()
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("a")],
                value=[
                    AST.Lambda(
                        parameters=[],
                        extra=None,
                        block=AST.Block(
                            statements=[
                                AST.Definition(
                                    const=False,
                                    var=[AST.Var("sum")],
                                    value=[AST.LitInt(0)],
                                ),
                                AST.ForLoop(
                                    var="i",
                                    start=AST.LitInt(1),
                                    end=AST.LitInt(11),
                                    step=AST.LitInt(1),
                                    block=AST.Block(
                                        statements=[
                                            AST.SetStatement(
                                                var=[AST.Access(AST.Var("sum"), None)],
                                                value=[
                                                    AST.BinaryExpression(
                                                        AST.BinExpType.ADD,
                                                        AST.Var("sum"),
                                                        AST.Var("i"),
                                                    )
                                                ],
                                            )
                                        ],
                                        return_statement=AST.LitNil(None),
                                    ),
                                ),
                            ],
                            return_statement=AST.Var("sum"),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("a"),
            args=[],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 55


def test_function_call_binds_parameters_and_returns_expression():
    # const add = function(a, b)
    #     return a + b
    # end
    # return add(2, 3)
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("add")],
                value=[
                    AST.Lambda(
                        parameters=["a", "b"],
                        extra=None,
                        block=AST.Block(
                            statements=[],
                            return_statement=AST.BinaryExpression(
                                AST.BinExpType.ADD,
                                AST.Var("a"),
                                AST.Var("b"),
                            ),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("add"),
            args=[AST.LitInt(2), AST.LitInt(3)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 5


def test_function_call_missing_arguments_are_bound_to_nil():
    # const missing_second = function(a, b)
    #     return b == nil
    # end
    # return missing_second(1)
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("missing_second")],
                value=[
                    AST.Lambda(
                        parameters=["a", "b"],
                        extra=None,
                        block=AST.Block(
                            statements=[],
                            return_statement=AST.BinaryExpression(
                                AST.BinExpType.EQUAL,
                                AST.Var("b"),
                                AST.LitNil(None),
                            ),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("missing_second"),
            args=[AST.LitInt(1)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result is True


def test_function_call_ignores_extra_arguments_without_extra_binding():
    # const first = function(a)
    #     return a
    # end
    # return first(1, 99)
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("first")],
                value=[
                    AST.Lambda(
                        parameters=["a"],
                        extra=None,
                        block=AST.Block(
                            statements=[],
                            return_statement=AST.Var("a"),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("first"),
            args=[AST.LitInt(1), AST.LitInt(99)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 1


def test_function_call_captures_extra_arguments_in_table():
    # const third_arg = function(first, ...rest)
    #     return rest[1]
    # end
    # return third_arg(10, 20, 30)
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("third_arg")],
                value=[
                    AST.Lambda(
                        parameters=["first"],
                        extra="rest",
                        block=AST.Block(
                            statements=[],
                            return_statement=AST.Access(AST.Var("rest"), AST.LitInt(1)),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("third_arg"),
            args=[AST.LitInt(10), AST.LitInt(20), AST.LitInt(30)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 30


def test_function_closure_reads_outer_variable():
    # let x = 10
    # const read_x = function()
    #     return x
    # end
    # set x = 11
    # return read_x()
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=False,
                var=[AST.Var("x")],
                value=[AST.LitInt(10)],
            ),
            AST.Definition(
                const=True,
                var=[AST.Var("read_x")],
                value=[
                    AST.Lambda(
                        parameters=[],
                        extra=None,
                        block=AST.Block(
                            statements=[],
                            return_statement=AST.Var("x"),
                        ),
                    )
                ],
            ),
            AST.SetStatement(
                var=[AST.Access(AST.Var("x"), None)],
                value=[AST.LitInt(11)],
            ),
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("read_x"),
            args=[],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 11


def test_function_closure_can_update_outer_variable():
    # let count = 0
    # const inc = function()
    #     set count = count + 1
    #     return count
    # end
    # return inc() + inc()
    inc_call = AST.FunctionCall(method=False, source=AST.Var("inc"), args=[])
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=False,
                var=[AST.Var("count")],
                value=[AST.LitInt(0)],
            ),
            AST.Definition(
                const=True,
                var=[AST.Var("inc")],
                value=[
                    AST.Lambda(
                        parameters=[],
                        extra=None,
                        block=AST.Block(
                            statements=[
                                AST.SetStatement(
                                    var=[AST.Access(AST.Var("count"), None)],
                                    value=[
                                        AST.BinaryExpression(
                                            AST.BinExpType.ADD,
                                            AST.Var("count"),
                                            AST.LitInt(1),
                                        )
                                    ],
                                )
                            ],
                            return_statement=AST.Var("count"),
                        ),
                    )
                ],
            ),
        ],
        return_statement=AST.BinaryExpression(
            AST.BinExpType.ADD,
            inc_call,
            inc_call,
        ),
    )

    result, env = eval_file(ast_file)

    assert result == 3
    assert env.get("count") == 2


def test_function_closure_returned_from_function_keeps_captured_scope():
    # const make_adder = function(x)
    #     return function(y)
    #         return x + y
    #     end
    # end
    # const add_five = make_adder(5)
    # return add_five(3)
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("make_adder")],
                value=[
                    AST.Lambda(
                        parameters=["x"],
                        extra=None,
                        block=AST.Block(
                            statements=[],
                            return_statement=AST.Lambda(
                                parameters=["y"],
                                extra=None,
                                block=AST.Block(
                                    statements=[],
                                    return_statement=AST.BinaryExpression(
                                        AST.BinExpType.ADD,
                                        AST.Var("x"),
                                        AST.Var("y"),
                                    ),
                                ),
                            ),
                        ),
                    )
                ],
            ),
            AST.Definition(
                const=True,
                var=[AST.Var("add_five")],
                value=[
                    AST.FunctionCall(
                        method=False,
                        source=AST.Var("make_adder"),
                        args=[AST.LitInt(5)],
                    )
                ],
            ),
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Var("add_five"),
            args=[AST.LitInt(3)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 8


def test_method_call_passes_receiver_as_first_argument():
    # const obj = {
    #     "base": 10,
    #     "add": function(self, x)
    #         return self.base + x
    #     end,
    # }
    # return obj:add(5)
    method = AST.Lambda(
        parameters=["self", "x"],
        extra=None,
        block=AST.Block(
            statements=[],
            return_statement=AST.BinaryExpression(
                AST.BinExpType.ADD,
                AST.Access(AST.Var("self"), AST.LitString("base")),
                AST.Var("x"),
            ),
        ),
    )
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("obj")],
                value=[
                    AST.LitTable(
                        [
                            (AST.LitString("base"), AST.LitInt(10)),
                            (AST.LitString("add"), method),
                        ]
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=True,
            source=AST.Access(AST.Var("obj"), AST.LitString("add")),
            args=[AST.LitInt(5)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 15


def test_normal_dot_call_does_not_pass_receiver():
    # const obj = {
    #     "id": function(x)
    #         return x
    #     end,
    # }
    # return obj.id(7)
    method = AST.Lambda(
        parameters=["x"],
        extra=None,
        block=AST.Block(
            statements=[],
            return_statement=AST.Var("x"),
        ),
    )
    ast_file = AST.Block(
        statements=[
            AST.Definition(
                const=True,
                var=[AST.Var("obj")],
                value=[
                    AST.LitTable(
                        [
                            (AST.LitString("id"), method),
                        ]
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(
            method=False,
            source=AST.Access(AST.Var("obj"), AST.LitString("id")),
            args=[AST.LitInt(7)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 7

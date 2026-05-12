import pytest

import xyz.parser.ast as AST

from xyz.interpreter.interpreter import XYZInterpreter
from xyz.interpreter.scoped_env import Scope

dummyspan = ((0,0),(0,0))


def scope(values: dict | None = None) -> Scope:
    env = Scope(None, "test")
    for name, value in (values or {}).items():
        env.define(name, value)
    return env


def scope_values(env: Scope):
    return {name: var.value for name, var in env.table.items()}


def eval_expr(expr: AST.Expression, global_var_table: dict | Scope | None = None):
    env = global_var_table if isinstance(global_var_table, Scope) else scope(global_var_table)
    interpreter = XYZInterpreter(env)
    return interpreter.eval_expression(expr)


def exec_stmt(statement: AST.Statement, global_var_table: dict | Scope | None = None):
    env = global_var_table if isinstance(global_var_table, Scope) else scope(global_var_table)
    interpreter = XYZInterpreter(env)
    interpreter.exec_statement(statement)
    return interpreter.GVT


def eval_file(ast_file: AST.File, global_var_table: dict | Scope | None = None):
    env = global_var_table if isinstance(global_var_table, Scope) else scope(global_var_table)
    interpreter = XYZInterpreter(env)
    return interpreter.execute_ast(ast_file), interpreter.GVT


ACCESS_AND_DEFINITION_AST = AST.Block(dummyspan,
    statements=[
        AST.Definition(dummyspan,
            const=False,
            var=[AST.Var(dummyspan,"a")],
            value=[
                AST.LitTable(dummyspan,
                    [
                        (
                            AST.LitString(dummyspan,"k"),
                            AST.LitTable(dummyspan,[(AST.LitString(dummyspan,"b"), AST.LitInt(dummyspan,99))]),
                        )
                    ]
                )
            ],
        ),
        AST.Definition(dummyspan,
            const=True,
            var=[AST.Var(dummyspan,"fx_result")],
            value=[
                AST.LitTable(dummyspan,
                    [
                        (AST.LitString(dummyspan,"c"), AST.LitString(dummyspan,"k")),
                    ]
                )
            ],
        ),
        AST.SetStatement(dummyspan,
            [
                AST.Access(dummyspan,
                    AST.Access(dummyspan,
                        AST.Var(dummyspan,"a"),
                        AST.Access(dummyspan,AST.Var(dummyspan,"fx_result"), AST.LitString(dummyspan,"c")),
                    ),
                    AST.LitString(dummyspan,"b"),
                )
            ],
            [AST.LitInt(dummyspan,10)],
        ),
    ],
    return_statement=AST.Access(dummyspan,
        AST.Access(dummyspan,
            AST.Var(dummyspan,"a"),
            AST.Access(dummyspan,AST.Var(dummyspan,"fx_result"), AST.LitString(dummyspan,"c")),
        ),
        AST.LitString(dummyspan,"b"),
    ),
)


# Source shape:
# let a = {"k": {"b": 99}}
# const fx_result = {"c": "k"}
# a[fx_result.c].b = 10
# return a[fx_result.c].b


def literal(value):
    if value is True:
        return AST.LitTrue(dummyspan,True)
    if value is False:
        return AST.LitFalse(dummyspan,False)
    if value is None:
        return AST.LitNil(dummyspan,None)
    if isinstance(value, int):
        return AST.LitInt(dummyspan,value)
    if isinstance(value, float):
        return AST.LitFloat(dummyspan,value)
    return AST.LitString(dummyspan,value)


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (AST.LitFalse(dummyspan,False), False),
        (AST.LitTrue(dummyspan,True), True),
        (AST.LitNil(dummyspan,None), None),
        (AST.LitInt(dummyspan,12), 12),
        (AST.LitFloat(dummyspan,12.34), 12.34),
        (AST.LitString(dummyspan,"hello"), "hello"),
    ],
)
def test_evaluates_literal_expressions(expr, expected):
    # Source expressions covered: false, true, nil, 12, 12.34, "hello"
    assert eval_expr(expr) == expected


def test_evaluates_table_expression():
    # return {"name": "xyz", 1: true}
    expr = AST.LitTable(dummyspan,
        [
            (AST.LitString(dummyspan,"name"), AST.LitString(dummyspan,"xyz")),
            (AST.LitInt(dummyspan,1), AST.LitTrue(dummyspan,True)),
        ]
    )

    assert eval_expr(expr) == {"name": "xyz", 1: True}


@pytest.mark.parametrize(
    ("expr", "expected"),
    [
        (AST.UnaryExpression(dummyspan,AST.UnExpType.NOT, AST.LitTrue(dummyspan,True)), False),
        (AST.UnaryExpression(dummyspan,AST.UnExpType.NOT, AST.LitFalse(dummyspan,False)), True),
        (AST.UnaryExpression(dummyspan,AST.UnExpType.NOT, AST.LitNil(dummyspan,None)), True),
        (AST.UnaryExpression(dummyspan,AST.UnExpType.NEG, AST.LitInt(dummyspan,10)), -10),
        (
            AST.UnaryExpression(dummyspan,
                AST.UnExpType.SIZE,
                AST.LitTable(dummyspan,[(AST.LitString(dummyspan,"key"), AST.LitInt(dummyspan,1))]),
            ),
            1,
        ),
    ],
)
def test_evaluates_unary_expressions(expr, expected):
    # Source expressions covered: !true, !false, !nil, -10, #{"key": 1}
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
    # Source expressions covered: 7 + 3, 7 - 3, 7 * 3, 7 / 2,
    # 7 // 2, 2 ** 3, 7 % 3, comparisons, bit ops, shifts,
    # equality, and/or, and "x" .. 7.
    expr = AST.BinaryExpression(dummyspan,
        operator,
        literal(left),
        literal(right),
    )

    assert eval_expr(expr) == expected


def test_evaluates_var_expression_from_global_var_table():
    # let answer = 42
    # return answer
    assert eval_expr(AST.Var(dummyspan,"answer"), {"answer": 42}) == 42


def test_evaluates_access_expression():
    # let table_name = {"field": 99}
    # return table_name.field
    expr = AST.Access(dummyspan,AST.Var(dummyspan,"table_name"), AST.LitString(dummyspan,"field"))
    assert eval_expr(expr, {"table_name": {"field": 99}}) == 99


def test_evaluates_nested_access_chain_with_access_as_index():
    # let a = {"k": {"b": 99}}
    # let fx_result = {"c": "k"}
    # return a[fx_result.c].b
    expr = AST.Access(dummyspan,
        AST.Access(dummyspan,
            AST.Var(dummyspan,"a"),
            AST.Access(dummyspan,
                AST.Var(dummyspan,"fx_result"),
                AST.LitString(dummyspan,"c"),
            ),
        ),
        AST.LitString(dummyspan,"b"),
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
    # let a = {"k": {"b": 99}}
    # const fx_result = {"c": "k"}
    # a[fx_result.c].b = 10
    # return a[fx_result.c].b
    result, env = eval_file(ACCESS_AND_DEFINITION_AST)

    assert result == 10
    assert scope_values(env) == {
        "a": {"k": {"b": 10}},
        "fx_result": {"c": "k"},
    }


def test_definition_creates_let_variable():
    # let a = 10
    statement = AST.Definition(dummyspan,
        const=False,
        var=[AST.Var(dummyspan,"a")],
        value=[AST.LitInt(dummyspan,10)],
    )

    env = exec_stmt(statement)

    assert env.get("a") == 10
    assert env.resolve_var("a").const is False


def test_definition_creates_const_variable():
    # const a = 10
    statement = AST.Definition(dummyspan,
        const=True,
        var=[AST.Var(dummyspan,"a")],
        value=[AST.LitInt(dummyspan,10)],
    )

    env = exec_stmt(statement)

    assert env.get("a") == 10
    assert env.resolve_var("a").const is True


def test_definition_creates_multiple_variables():
    # let a, b = 1, "two"
    statement = AST.Definition(dummyspan,
        const=False,
        var=[AST.Var(dummyspan,"a"), AST.Var(dummyspan,"b")],
        value=[AST.LitInt(dummyspan,1), AST.LitString(dummyspan,"two")],
    )

    assert scope_values(exec_stmt(statement)) == {"a": 1, "b": "two"}


def test_set_statement_replaces_existing_variable():
    # let a = 10
    # a = 20
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.Var(dummyspan,"a"), None)],
        [AST.LitInt(dummyspan,20)],
    )

    assert exec_stmt(statement, {"a": 10}).get("a") == 20


def test_set_statement_evaluates_value_expression_before_assignment():
    # let a = 0
    # a = 2 + 3
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.Var(dummyspan,"a"), None)],
        [
            AST.BinaryExpression(dummyspan,
                AST.BinExpType.ADD,
                AST.LitInt(dummyspan,2),
                AST.LitInt(dummyspan,3),
            )
        ],
    )

    assert exec_stmt(statement, {"a": 0}).get("a") == 5


def test_set_statement_assigns_into_existing_table():
    # let a = {}
    # a.b = 10
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.Var(dummyspan,"a"), AST.LitString(dummyspan,"b"))],
        [AST.LitInt(dummyspan,10)],
    )

    assert scope_values(exec_stmt(statement, {"a": {}})) == {"a": {"b": 10}}


def test_set_statement_assigns_into_nested_access_target():
    # let a = {"b": {}}
    # a.b.c = 10
    statement = AST.SetStatement(dummyspan,
        [
            AST.Access(dummyspan,
                AST.Access(dummyspan,AST.Var(dummyspan,"a"), AST.LitString(dummyspan,"b")),
                AST.LitString(dummyspan,"c"),
            )
        ],
        [AST.LitInt(dummyspan,10)],
    )

    assert scope_values(exec_stmt(statement, {"a": {"b": {}}})) == {
        "a": {"b": {"c": 10}}
    }


def test_set_statement_assigns_with_access_expression_as_index():
    # let a = {"k": 1}
    # let fx_result = {"c": "k"}
    # a[fx_result.c] = 10
    statement = AST.SetStatement(dummyspan,
        [
            AST.Access(dummyspan,
                AST.Var(dummyspan,"a"),
                AST.Access(dummyspan,AST.Var(dummyspan,"fx_result"), AST.LitString(dummyspan,"c")),
            )
        ],
        [AST.LitInt(dummyspan,10)],
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
    # let a = {"k": {"b": 99}}
    # let fx_result = {"c": "k"}
    # a[fx_result.c].b = 10
    statement = AST.SetStatement(dummyspan,
        [
            AST.Access(dummyspan,
                AST.Access(dummyspan,
                    AST.Var(dummyspan,"a"),
                    AST.Access(dummyspan,AST.Var(dummyspan,"fx_result"), AST.LitString(dummyspan,"c")),
                ),
                AST.LitString(dummyspan,"b"),
            )
        ],
        [AST.LitInt(dummyspan,10)],
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
    # let a = 0
    # let table = {}
    # a, table.field = 1, "value"
    statement = AST.SetStatement(dummyspan,
        [
            AST.Access(dummyspan,AST.Var(dummyspan,"a"), None),
            AST.Access(dummyspan,AST.Var(dummyspan,"table"), AST.LitString(dummyspan,"field")),
        ],
        [
            AST.LitInt(dummyspan,1),
            AST.LitString(dummyspan,"value"),
        ],
    )

    assert scope_values(exec_stmt(statement, {"a": 0, "table": {}})) == {
        "a": 1,
        "table": {"field": "value"},
    }


def test_set_statement_rejects_unbound_variable_assignment():
    # a = 1
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.Var(dummyspan,"a"), None)],
        [AST.LitInt(dummyspan,1)],
    )

    with pytest.raises(RuntimeError, match="unbound variable"):
        exec_stmt(statement)


def test_set_statement_rejects_const_variable_reassignment():
    # const a = 1
    # a = 2
    env = scope()
    env.define("a", 1, const=True)
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.Var(dummyspan,"a"), None)],
        [AST.LitInt(dummyspan,2)],
    )

    with pytest.raises(RuntimeError, match="const variable"):
        exec_stmt(statement, env)


def test_set_statement_can_mutate_table_stored_in_const_variable():
    # const a = {"b": 1}
    # a.b = 2
    env = scope()
    env.define("a", {"b": 1}, const=True)
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.Var(dummyspan,"a"), AST.LitString(dummyspan,"b"))],
        [AST.LitInt(dummyspan,2)],
    )

    assert scope_values(exec_stmt(statement, env)) == {"a": {"b": 2}}


def test_set_statement_rejects_mismatched_target_and_value_counts():
    # a, b = 1
    statement = AST.SetStatement(dummyspan,
        [
            AST.Access(dummyspan,AST.Var(dummyspan,"a"), None),
            AST.Access(dummyspan,AST.Var(dummyspan,"b"), None),
        ],
        [AST.LitInt(dummyspan,1)],
    )

    with pytest.raises(RuntimeError, match="same number"):
        exec_stmt(statement)


def test_definition_rejects_mismatched_target_and_value_counts():
    # let a, b = 1
    statement = AST.Definition(dummyspan,
        const=False,
        var=[AST.Var(dummyspan,"a"), AST.Var(dummyspan,"b")],
        value=[AST.LitInt(dummyspan,1)],
    )

    with pytest.raises(RuntimeError, match="same number"):
        exec_stmt(statement)


def test_set_statement_rejects_no_index_target_that_is_not_a_variable():
    # Invalid lowered AST, roughly trying to assign to a literal target:
    # "not_a_var" = 1
    statement = AST.SetStatement(dummyspan,
        [AST.Access(dummyspan,AST.LitString(dummyspan,"not_a_var"), None)],
        [AST.LitInt(dummyspan,1)],
    )

    with pytest.raises(AssertionError, match="must be a variable"):
        exec_stmt(statement)


def test_for_loop_updates_outer_variable():
    # let sum = 0
    # for i = 1, 4, 1 do
    #     sum = sum + i
    # end
    # return sum
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"sum")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.ForLoop(dummyspan,
                var="i",
                start=AST.LitInt(dummyspan,1),
                end=AST.LitInt(dummyspan,4),
                step=AST.LitInt(dummyspan,1),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"sum"), None)],
                            value=[
                                AST.BinaryExpression(dummyspan,
                                    AST.BinExpType.ADD,
                                    AST.Var(dummyspan,"sum"),
                                    AST.Var(dummyspan,"i"),
                                )
                            ],
                        )
                    ],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.Var(dummyspan,"sum"),
    )

    result, env = eval_file(ast_file)

    assert result == 6
    assert scope_values(env) == {"sum": 6}


def test_for_loop_variable_is_not_visible_after_loop():
    # for i = 1, 2, 1 do
    # end
    # return i
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.ForLoop(dummyspan,
                var="i",
                start=AST.LitInt(dummyspan,1),
                end=AST.LitInt(dummyspan,2),
                step=AST.LitInt(dummyspan,1),
                block=AST.Block(dummyspan,
                    statements=[],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.Var(dummyspan,"i"),
    )

    with pytest.raises(RuntimeError, match="unbound variable"):
        eval_file(ast_file)


def test_for_loop_does_not_run_body_when_range_is_empty():
    # let sum = 0
    # for i = 4, 1, 1 do
    #     sum = 99
    # end
    # return sum
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"sum")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.ForLoop(dummyspan,
                var="i",
                start=AST.LitInt(dummyspan,4),
                end=AST.LitInt(dummyspan,1),
                step=AST.LitInt(dummyspan,1),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"sum"), None)],
                            value=[AST.LitInt(dummyspan,99)],
                        )
                    ],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.Var(dummyspan,"sum"),
    )

    result, env = eval_file(ast_file)

    assert result == 0
    assert scope_values(env) == {"sum": 0}


def test_break_exits_nearest_for_loop_and_continues_after_loop():
    # let sum = 0
    # for i = 1, 10, 1 do
    #     sum = sum + i
    #     break
    #     sum = 999
    # end
    # sum = sum + 10
    # return sum
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"sum")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.ForLoop(dummyspan,
                var="i",
                start=AST.LitInt(dummyspan,1),
                end=AST.LitInt(dummyspan,10),
                step=AST.LitInt(dummyspan,1),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"sum"), None)],
                            value=[
                                AST.BinaryExpression(dummyspan,
                                    AST.BinExpType.ADD,
                                    AST.Var(dummyspan,"sum"),
                                    AST.Var(dummyspan,"i"),
                                )
                            ],
                        ),
                        AST.Break(dummyspan,),
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"sum"), None)],
                            value=[AST.LitInt(dummyspan,999)],
                        ),
                    ],
                    return_statement=None,
                ),
            ),
            AST.SetStatement(dummyspan,
                var=[AST.Access(dummyspan,AST.Var(dummyspan,"sum"), None)],
                value=[
                    AST.BinaryExpression(dummyspan,
                        AST.BinExpType.ADD,
                        AST.Var(dummyspan,"sum"),
                        AST.LitInt(dummyspan,10),
                    )
                ],
            ),
        ],
        return_statement=AST.Var(dummyspan,"sum"),
    )

    result, env = eval_file(ast_file)

    assert result == 11
    assert scope_values(env) == {"sum": 11}


def test_function_sums_one_to_ten_and_returns_result():
    # const a = function()
    #     let sum = 0
    #     for i = 1, 11, 1 do
    #         sum = sum + i
    #     end
    #     return sum
    # end
    # return a()
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"a")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=[],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[
                                AST.Definition(dummyspan,
                                    const=False,
                                    var=[AST.Var(dummyspan,"sum")],
                                    value=[AST.LitInt(dummyspan,0)],
                                ),
                                AST.ForLoop(dummyspan,
                                    var="i",
                                    start=AST.LitInt(dummyspan,1),
                                    end=AST.LitInt(dummyspan,11),
                                    step=AST.LitInt(dummyspan,1),
                                    block=AST.Block(dummyspan,
                                        statements=[
                                            AST.SetStatement(dummyspan,
                                                var=[AST.Access(dummyspan,AST.Var(dummyspan,"sum"), None)],
                                                value=[
                                                    AST.BinaryExpression(dummyspan,
                                                        AST.BinExpType.ADD,
                                                        AST.Var(dummyspan,"sum"),
                                                        AST.Var(dummyspan,"i"),
                                                    )
                                                ],
                                            )
                                        ],
                                        return_statement=None,
                                    ),
                                ),
                            ],
                            return_statement=AST.Var(dummyspan,"sum"),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"a"),
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
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"add")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=["a", "b"],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[],
                            return_statement=AST.BinaryExpression(dummyspan,
                                AST.BinExpType.ADD,
                                AST.Var(dummyspan,"a"),
                                AST.Var(dummyspan,"b"),
                            ),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"add"),
            args=[AST.LitInt(dummyspan,2), AST.LitInt(dummyspan,3)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 5


def test_function_call_missing_arguments_are_bound_to_nil():
    # const missing_second = function(a, b)
    #     return b == nil
    # end
    # return missing_second(1)
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"missing_second")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=["a", "b"],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[],
                            return_statement=AST.BinaryExpression(dummyspan,
                                AST.BinExpType.EQUAL,
                                AST.Var(dummyspan,"b"),
                                AST.LitNil(dummyspan,None),
                            ),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"missing_second"),
            args=[AST.LitInt(dummyspan,1)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result is True


def test_function_call_ignores_extra_arguments_without_extra_binding():
    # const first = function(a)
    #     return a
    # end
    # return first(1, 99)
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"first")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=["a"],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[],
                            return_statement=AST.Var(dummyspan,"a"),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"first"),
            args=[AST.LitInt(dummyspan,1), AST.LitInt(dummyspan,99)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 1


def test_function_call_captures_extra_arguments_in_table():
    # const third_arg = function(first, ...rest)
    #     return rest[1]
    # end
    # return third_arg(10, 20, 30)
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"third_arg")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=["first"],
                        extra="rest",
                        block=AST.Block(dummyspan,
                            statements=[],
                            return_statement=AST.Access(dummyspan,AST.Var(dummyspan,"rest"), AST.LitInt(dummyspan,1)),
                        ),
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"third_arg"),
            args=[AST.LitInt(dummyspan,10), AST.LitInt(dummyspan,20), AST.LitInt(dummyspan,30)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 30


def test_function_closure_reads_outer_variable():
    # let x = 10
    # const read_x = function()
    #     return x
    # end
    # x = 11
    # return read_x()
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"x")],
                value=[AST.LitInt(dummyspan,10)],
            ),
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"read_x")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=[],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[],
                            return_statement=AST.Var(dummyspan,"x"),
                        ),
                    )
                ],
            ),
            AST.SetStatement(dummyspan,
                var=[AST.Access(dummyspan,AST.Var(dummyspan,"x"), None)],
                value=[AST.LitInt(dummyspan,11)],
            ),
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"read_x"),
            args=[],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 11


def test_function_closure_can_update_outer_variable():
    # let count = 0
    # const inc = function()
    #     count = count + 1
    #     return count
    # end
    # return inc() + inc()
    inc_call = AST.FunctionCall(dummyspan,method=False, source=AST.Var(dummyspan,"inc"), args=[])
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"count")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"inc")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=[],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                                    value=[
                                        AST.BinaryExpression(dummyspan,
                                            AST.BinExpType.ADD,
                                            AST.Var(dummyspan,"count"),
                                            AST.LitInt(dummyspan,1),
                                        )
                                    ],
                                )
                            ],
                            return_statement=AST.Var(dummyspan,"count"),
                        ),
                    )
                ],
            ),
        ],
        return_statement=AST.BinaryExpression(dummyspan,
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
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"make_adder")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=["x"],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[],
                            return_statement=AST.Lambda(dummyspan,
                                parameters=["y"],
                                extra=None,
                                block=AST.Block(dummyspan,
                                    statements=[],
                                    return_statement=AST.BinaryExpression(dummyspan,
                                        AST.BinExpType.ADD,
                                        AST.Var(dummyspan,"x"),
                                        AST.Var(dummyspan,"y"),
                                    ),
                                ),
                            ),
                        ),
                    )
                ],
            ),
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"add_five")],
                value=[
                    AST.FunctionCall(dummyspan,
                        method=False,
                        source=AST.Var(dummyspan,"make_adder"),
                        args=[AST.LitInt(dummyspan,5)],
                    )
                ],
            ),
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Var(dummyspan,"add_five"),
            args=[AST.LitInt(dummyspan,3)],
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
    method = AST.Lambda(dummyspan,
        parameters=["self", "x"],
        extra=None,
        block=AST.Block(dummyspan,
            statements=[],
            return_statement=AST.BinaryExpression(dummyspan,
                AST.BinExpType.ADD,
                AST.Access(dummyspan,AST.Var(dummyspan,"self"), AST.LitString(dummyspan,"base")),
                AST.Var(dummyspan,"x"),
            ),
        ),
    )
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"obj")],
                value=[
                    AST.LitTable(dummyspan,
                        [
                            (AST.LitString(dummyspan,"base"), AST.LitInt(dummyspan,10)),
                            (AST.LitString(dummyspan,"add"), method),
                        ]
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=True,
            source=AST.Access(dummyspan,AST.Var(dummyspan,"obj"), AST.LitString(dummyspan,"add")),
            args=[AST.LitInt(dummyspan,5)],
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
    method = AST.Lambda(dummyspan,
        parameters=["x"],
        extra=None,
        block=AST.Block(dummyspan,
            statements=[],
            return_statement=AST.Var(dummyspan,"x"),
        ),
    )
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"obj")],
                value=[
                    AST.LitTable(dummyspan,
                        [
                            (AST.LitString(dummyspan,"id"), method),
                        ]
                    )
                ],
            )
        ],
        return_statement=AST.FunctionCall(dummyspan,
            method=False,
            source=AST.Access(dummyspan,AST.Var(dummyspan,"obj"), AST.LitString(dummyspan,"id")),
            args=[AST.LitInt(dummyspan,7)],
        ),
    )

    result, _ = eval_file(ast_file)

    assert result == 7


def test_function_call_statement_runs_for_side_effects_and_ignores_return_value():
    # let count = 0
    # const inc = function()
    #     count = count + 1
    #     return 999
    # end
    # inc()
    # return count
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"count")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"inc")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=[],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                                    value=[
                                        AST.BinaryExpression(dummyspan,
                                            AST.BinExpType.ADD,
                                            AST.Var(dummyspan,"count"),
                                            AST.LitInt(dummyspan,1),
                                        )
                                    ],
                                )
                            ],
                            return_statement=AST.LitInt(dummyspan,999),
                        ),
                    )
                ],
            ),
            AST.FunctionCall(dummyspan,
                method=False,
                source=AST.Var(dummyspan,"inc"),
                args=[],
            ),
        ],
        return_statement=AST.Var(dummyspan,"count"),
    )

    result, env = eval_file(ast_file)

    assert result == 1
    assert env.get("count") == 1


def test_block_statement_uses_inner_scope_and_can_update_outer_variable():
    # let outer = 1
    # do
    #     let inner = 10
    #     outer = outer + inner
    # end
    # return outer
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"outer")],
                value=[AST.LitInt(dummyspan,1)],
            ),
            AST.Block(dummyspan,
                statements=[
                    AST.Definition(dummyspan,
                        const=False,
                        var=[AST.Var(dummyspan,"inner")],
                        value=[AST.LitInt(dummyspan,10)],
                    ),
                    AST.SetStatement(dummyspan,
                        var=[AST.Access(dummyspan,AST.Var(dummyspan,"outer"), None)],
                        value=[
                            AST.BinaryExpression(dummyspan,
                                AST.BinExpType.ADD,
                                AST.Var(dummyspan,"outer"),
                                AST.Var(dummyspan,"inner"),
                            )
                        ],
                    ),
                ],
                return_statement=None,
            ),
        ],
        return_statement=AST.Var(dummyspan,"outer"),
    )

    result, env = eval_file(ast_file)

    assert result == 11
    assert scope_values(env) == {"outer": 11}
    with pytest.raises(RuntimeError, match="unbound variable"):
        env.get("inner")


def test_while_loop_runs_until_condition_is_false():
    # let count = 0
    # while count < 3 do
    #     count = count + 1
    # end
    # return count
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"count")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.WhileLoop(dummyspan,
                condition=AST.BinaryExpression(dummyspan,
                    AST.BinExpType.LESS,
                    AST.Var(dummyspan,"count"),
                    AST.LitInt(dummyspan,3),
                ),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                            value=[
                                AST.BinaryExpression(dummyspan,
                                    AST.BinExpType.ADD,
                                    AST.Var(dummyspan,"count"),
                                    AST.LitInt(dummyspan,1),
                                )
                            ],
                        )
                    ],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.Var(dummyspan,"count"),
    )

    result, env = eval_file(ast_file)

    assert result == 3
    assert scope_values(env) == {"count": 3}


def test_while_loop_break_exits_loop_and_continues_after_loop():
    # let count = 0
    # while true do
    #     count = count + 1
    #     break
    #     count = 999
    # end
    # count = count + 10
    # return count
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"count")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.WhileLoop(dummyspan,
                condition=AST.LitTrue(dummyspan,True),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                            value=[
                                AST.BinaryExpression(dummyspan,
                                    AST.BinExpType.ADD,
                                    AST.Var(dummyspan,"count"),
                                    AST.LitInt(dummyspan,1),
                                )
                            ],
                        ),
                        AST.Break(dummyspan,),
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                            value=[AST.LitInt(dummyspan,999)],
                        ),
                    ],
                    return_statement=None,
                ),
            ),
            AST.SetStatement(dummyspan,
                var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                value=[
                    AST.BinaryExpression(dummyspan,
                        AST.BinExpType.ADD,
                        AST.Var(dummyspan,"count"),
                        AST.LitInt(dummyspan,10),
                    )
                ],
            ),
        ],
        return_statement=AST.Var(dummyspan,"count"),
    )

    result, env = eval_file(ast_file)

    assert result == 11
    assert scope_values(env) == {"count": 11}


def test_repeat_loop_runs_body_at_least_once_and_break_exits():
    # let count = 0
    # repeat
    #     count = count + 1
    #     break
    # until true
    # return count
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"count")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.RepeatLoop(dummyspan,
                condition=AST.LitTrue(dummyspan,True),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                            value=[
                                AST.BinaryExpression(dummyspan,
                                    AST.BinExpType.ADD,
                                    AST.Var(dummyspan,"count"),
                                    AST.LitInt(dummyspan,1),
                                )
                            ],
                        ),
                        AST.Break(dummyspan,),
                    ],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.Var(dummyspan,"count"),
    )

    result, env = eval_file(ast_file)

    assert result == 1
    assert scope_values(env) == {"count": 1}


def test_if_statement_executes_first_truthy_branch_only():
    # let value = 0
    # if false then
    #     value = 1
    # elseif true then
    #     value = 2
    # elseif true then
    #     value = 3
    # end
    # return value
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"value")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.IfStatement(dummyspan,
                conditions=[
                    (
                        AST.LitFalse(dummyspan,False),
                        AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[AST.Access(dummyspan,AST.Var(dummyspan,"value"), None)],
                                    value=[AST.LitInt(dummyspan,1)],
                                )
                            ],
                            return_statement=None,
                        ),
                    ),
                    (
                        AST.LitTrue(dummyspan,True),
                        AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[AST.Access(dummyspan,AST.Var(dummyspan,"value"), None)],
                                    value=[AST.LitInt(dummyspan,2)],
                                )
                            ],
                            return_statement=None,
                        ),
                    ),
                    (
                        AST.LitTrue(dummyspan,True),
                        AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[AST.Access(dummyspan,AST.Var(dummyspan,"value"), None)],
                                    value=[AST.LitInt(dummyspan,3)],
                                )
                            ],
                            return_statement=None,
                        ),
                    ),
                ],
                else_block=None,
            ),
        ],
        return_statement=AST.Var(dummyspan,"value"),
    )

    result, env = eval_file(ast_file)

    assert result == 2
    assert scope_values(env) == {"value": 2}


def test_if_statement_executes_else_when_no_condition_matches():
    # let value = 0
    # if false then
    #     value = 1
    # else
    #     value = 4
    # end
    # return value
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=False,
                var=[AST.Var(dummyspan,"value")],
                value=[AST.LitInt(dummyspan,0)],
            ),
            AST.IfStatement(dummyspan,
                conditions=[
                    (
                        AST.LitFalse(dummyspan,False),
                        AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[AST.Access(dummyspan,AST.Var(dummyspan,"value"), None)],
                                    value=[AST.LitInt(dummyspan,1)],
                                )
                            ],
                            return_statement=None,
                        ),
                    )
                ],
                else_block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"value"), None)],
                            value=[AST.LitInt(dummyspan,4)],
                        )
                    ],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.Var(dummyspan,"value"),
    )

    result, env = eval_file(ast_file)

    assert result == 4
    assert scope_values(env) == {"value": 4}



def test_unary_neg_rejects_non_numeric_values():
    # return -"x"
    with pytest.raises(AssertionError, match="attempt to perform arithmetic"):
        eval_expr(AST.UnaryExpression(dummyspan,AST.UnExpType.NEG, AST.LitString(dummyspan,"x")))


def test_unary_size_rejects_non_table_values():
    # return #"x"
    with pytest.raises(AssertionError, match="attempt to get length"):
        eval_expr(AST.UnaryExpression(dummyspan,AST.UnExpType.SIZE, AST.LitString(dummyspan,"x")))


def test_function_call_rejects_non_function_source():
    # return 1()
    with pytest.raises(AssertionError, match="must be a function"):
        eval_expr(
            AST.FunctionCall(dummyspan,
                method=False,
                source=AST.LitInt(dummyspan,1),
                args=[],
            )
        )


def test_method_call_requires_access_source():
    # Invalid lowered AST, roughly:
    # return f:()
    # Method-call syntax should lower to an access source like obj:method().
    with pytest.raises(AssertionError, match="Expected function called with ':'"):
        eval_expr(
            AST.FunctionCall(dummyspan,
                method=True,
                source=AST.Var(dummyspan,"f"),
                args=[],
            ),
            {"f": 1},
        )


def test_complex_program_uses_functions_closures_methods_tables_loops_and_if():
    # const make_counter = function(start)
    #     let count = start
    #     return function(step)
    #         count = count + step
    #         return count
    #     end
    # end
    #
    # const account = {
    #     "balance": 10,
    #     "inc": make_counter(0),
    #     "deposit": function(self, amount)
    #         self.balance = self.balance + amount
    #         return self.balance
    #     end,
    # }
    #
    # for i = 1, 4, 1 do
    #     account.balance = account:deposit(account.inc(i))
    # end
    #
    # if account.balance > 30 then
    #     account.status = "high"
    # else
    #     account.status = "low"
    # end
    #
    # return account.status .. ":" .. account.balance
    inc_method = AST.Lambda(dummyspan,
        parameters=["self", "amount"],
        extra=None,
        block=AST.Block(dummyspan,
            statements=[
                AST.SetStatement(dummyspan,
                    var=[
                        AST.Access(dummyspan,
                            AST.Var(dummyspan,"self"),
                            AST.LitString(dummyspan,"balance"),
                        )
                    ],
                    value=[
                        AST.BinaryExpression(dummyspan,
                            AST.BinExpType.ADD,
                            AST.Access(dummyspan,AST.Var(dummyspan,"self"), AST.LitString(dummyspan,"balance")),
                            AST.Var(dummyspan,"amount"),
                        )
                    ],
                )
            ],
            return_statement=AST.Access(dummyspan,AST.Var(dummyspan,"self"), AST.LitString(dummyspan,"balance")),
        ),
    )
    ast_file = AST.Block(dummyspan,
        statements=[
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"make_counter")],
                value=[
                    AST.Lambda(dummyspan,
                        parameters=["start"],
                        extra=None,
                        block=AST.Block(dummyspan,
                            statements=[
                                AST.Definition(dummyspan,
                                    const=False,
                                    var=[AST.Var(dummyspan,"count")],
                                    value=[AST.Var(dummyspan,"start")],
                                )
                            ],
                            return_statement=AST.Lambda(dummyspan,
                                parameters=["step"],
                                extra=None,
                                block=AST.Block(dummyspan,
                                    statements=[
                                        AST.SetStatement(dummyspan,
                                            var=[AST.Access(dummyspan,AST.Var(dummyspan,"count"), None)],
                                            value=[
                                                AST.BinaryExpression(dummyspan,
                                                    AST.BinExpType.ADD,
                                                    AST.Var(dummyspan,"count"),
                                                    AST.Var(dummyspan,"step"),
                                                )
                                            ],
                                        )
                                    ],
                                    return_statement=AST.Var(dummyspan,"count"),
                                ),
                            ),
                        ),
                    )
                ],
            ),
            AST.Definition(dummyspan,
                const=True,
                var=[AST.Var(dummyspan,"account")],
                value=[
                    AST.LitTable(dummyspan,
                        [
                            (AST.LitString(dummyspan,"balance"), AST.LitInt(dummyspan,10)),
                            (
                                AST.LitString(dummyspan,"inc"),
                                AST.FunctionCall(dummyspan,
                                    method=False,
                                    source=AST.Var(dummyspan,"make_counter"),
                                    args=[AST.LitInt(dummyspan,0)],
                                ),
                            ),
                            (AST.LitString(dummyspan,"deposit"), inc_method),
                        ]
                    )
                ],
            ),
            AST.ForLoop(dummyspan,
                var="i",
                start=AST.LitInt(dummyspan,1),
                end=AST.LitInt(dummyspan,4),
                step=AST.LitInt(dummyspan,1),
                block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[
                                AST.Access(dummyspan,
                                    AST.Var(dummyspan,"account"),
                                    AST.LitString(dummyspan,"balance"),
                                )
                            ],
                            value=[
                                AST.FunctionCall(dummyspan,
                                    method=True,
                                    source=AST.Access(dummyspan,
                                        AST.Var(dummyspan,"account"),
                                        AST.LitString(dummyspan,"deposit"),
                                    ),
                                    args=[
                                        AST.FunctionCall(dummyspan,
                                            method=False,
                                            source=AST.Access(dummyspan,
                                                AST.Var(dummyspan,"account"),
                                                AST.LitString(dummyspan,"inc"),
                                            ),
                                            args=[AST.Var(dummyspan,"i")],
                                        )
                                    ],
                                )
                            ],
                        )
                    ],
                    return_statement=None,
                ),
            ),
            AST.IfStatement(dummyspan,
                conditions=[
                    (
                        AST.BinaryExpression(dummyspan,
                            AST.BinExpType.GREATER,
                            AST.Access(dummyspan,AST.Var(dummyspan,"account"), AST.LitString(dummyspan,"balance")),
                            AST.LitInt(dummyspan,30),
                        ),
                        AST.Block(dummyspan,
                            statements=[
                                AST.SetStatement(dummyspan,
                                    var=[
                                        AST.Access(dummyspan,
                                            AST.Var(dummyspan,"account"),
                                            AST.LitString(dummyspan,"status"),
                                        )
                                    ],
                                    value=[AST.LitString(dummyspan,"high")],
                                )
                            ],
                            return_statement=None,
                        ),
                    )
                ],
                else_block=AST.Block(dummyspan,
                    statements=[
                        AST.SetStatement(dummyspan,
                            var=[
                                AST.Access(dummyspan,
                                    AST.Var(dummyspan,"account"),
                                    AST.LitString(dummyspan,"status"),
                                )
                            ],
                            value=[AST.LitString(dummyspan,"low")],
                        )
                    ],
                    return_statement=None,
                ),
            ),
        ],
        return_statement=AST.BinaryExpression(dummyspan,
            AST.BinExpType.CONCAT,
            AST.BinaryExpression(dummyspan,
                AST.BinExpType.CONCAT,
                AST.Access(dummyspan,AST.Var(dummyspan,"account"), AST.LitString(dummyspan,"status")),
                AST.LitString(dummyspan,":"),
            ),
            AST.Access(dummyspan,AST.Var(dummyspan,"account"), AST.LitString(dummyspan,"balance")),
        ),
    )

    result, env = eval_file(ast_file)

    assert result == "low:20"
    assert env.get("account")["balance"] == 20
    assert env.get("account")["status"] == "low"

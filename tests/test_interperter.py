import pytest

@pytest.mark.parametrize(
    ("program", "expected"),
    [
        ("a", var("a")),
        ("_abc123", var("_abc123")),
        ("1", integer("1")),
        ("12.34", float_num("12.34")),
        ("true", AST.LitTrue(True)),
        ("false", AST.LitFalse(False)),
        ("nil", AST.LitNil(None)),
        ("(a)", grouped(var("a"))),
    ],
)
def test_interperting(program, expected):
    assert build_program(program) == expected

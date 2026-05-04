
import pytest

from main import build_program
from xyz.parser import AST

def test_unary():
    PROGRAM = '''!a'''
    EXPECTED_AST = AST.UnaryExpression(AST.UnExpType.NOT, AST.VarExpr('a'))
    assert EXPECTED_AST == build_program(PROGRAM)
    

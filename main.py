from sys import argv
from os.path import isfile
from io import StringIO

from xyz.tokenizer import tokenize
from xyz.parser import parse
from xyz.error import Error

from xyz.parser.token_iterator import TokenIterator
from io import StringIO

from xyz.interpreter.interpreter import XYZInterperter

import pytest # would be sad to have known failing tests
import xyz.parser.ast as AST

def build_program(file_data: StringIO):
    # need to pretend we are a file
    if isinstance(file_data, str):
        file_data = StringIO(file_data)

    result = tokenize(file_data)
    if isinstance(result, Error):
        result.print()
    else:
        tree = parse(file_data, TokenIterator(result))
        if isinstance(tree, Error):
            tree.print()
        else:
            print("\nResult from parsing: \n")
            print(tree)
    return tree

def run_tests():
    retcode = pytest.main(["tests/"])
    assert retcode == 0, "Tests failed! see output"

def main():

    interp = XYZInterperter()
    TEST_AST: AST.File = AST.Block(
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

    print(interp.execute_ast(TEST_AST))
    exit()
    
    run_tests() 

    if len(argv) < 2:
        print("No XYZ source file provided!")
    elif not isfile(argv[1]):
        print("File %s does not exist!" % argv[1])
    else:
        with open(argv[1], "r") as file:
            print("## IMPLEMENTATION STATUS - 2/3 (WIP)")
            print("## PRINTING PARSER OUTPUT")
            print()
            build_program(StringIO(file.read()))


if __name__ == "__main__":
    main()

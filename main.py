from sys import argv
from os.path import isfile
from io import StringIO

from xyz.tokenizer import tokenize
from xyz.parser import parse
from xyz.error import Error

from xyz.parser.token_iterator import TokenIterator
from io import StringIO

import pytest # would be sad to have known failing tests

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

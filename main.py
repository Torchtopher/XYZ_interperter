from sys import argv, stdin
from os.path import isfile
from enum import Enum

from xyz import eval, XYZEnvironment, display
from xyz.eval import debug, BuildStep

import pytest # would be sad to have known failing tests

DEBUG = True

# demo import function
def xyz_import(name):
    with open("examples/"+name, "r") as file:
        return eval(file.read(), ENV)

ENV = XYZEnvironment({
    "io": {
        "read": lambda: input(),
        "readchar": lambda: stdin.read(1),
        "print": lambda *args: print(*[display(a) for a in args]),
        "write": lambda x: print(display(x), end='')
    },
    "string": {
        "length": lambda x: len(str(x)),
        "char": lambda x, i: x[i],
        "from_codepoint": lambda c: chr(c),
        "to_codepoint": lambda c: ord(c or '\0'),
    },
    "import": xyz_import
})

def run_tests():
    retcode = pytest.main(["tests/"])
    assert retcode == 0, "Tests failed! see output"

def main():
    if DEBUG: run_tests() 

    if len(argv) < 2:
        print("No XYZ source file provided!")
    elif not isfile(argv[1]):
        print("File %s does not exist!" % argv[1])
    else:
        with open(argv[1], "r") as file:
            if DEBUG:
                debug(file.read(), BuildStep.PARSE, ENV)
            else:
                print(display(eval(file.read(), ENV)))


if __name__ == "__main__":
    main()

from sys import argv
from os.path import isfile
from enum import Enum

from xyz import eval, XYZEnvironment
from xyz.eval import debug, BuildStep

import pytest # would be sad to have known failing tests

DEBUG = False
ENV = XYZEnvironment({
    "io": {
        "print": lambda *args: print(*args)
    }
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
                debug(file.read(), BuildStep.EXECUTE, ENV)
            else:
                print(eval(file.read(), ENV))


if __name__ == "__main__":
    main()

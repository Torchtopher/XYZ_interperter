#!/usr/bin/env python3

# public API ("libxyz") in xyz module.
# this file is only for demonstration.

from io import StringIO
from sys import argv, stdin
from os.path import isfile
import os
from enum import Enum
from pathlib import Path

from xyz import eval, XYZEnvironment, display
from xyz.eval import debug, BuildStep
from xyz.error import XYZSource

current_dir: Path = Path(".")
DEBUG = os.environ.get("XYZ_DEBUG", "0") != "0"

def xyz_import(name: str):
    # since everything is synchronous, we can just store the
    # currently running file in current_dir and use this for relative imports.
    return run_file(Path(name))

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

def main():
    if len(argv) < 2:
        print("No XYZ source file provided!")
    else:
        run_file(Path(argv[1]))

def run_file(path: Path):
    global current_dir
    original: Path = current_dir
    current_dir = current_dir.joinpath(path.parent)
    current_file = current_dir.joinpath(path.name)
    if not isfile(current_file):
        print("File %s does not exist" % current_file)
    else:
        with open(current_file, "r") as file:
            source = XYZSource(StringIO(file.read()), current_file.name)
            if DEBUG:
                result = debug(source, BuildStep.EXECUTE, ENV)
            else:
                result = eval(source, ENV)
    current_dir = original
    return result

if __name__ == "__main__":
    main()

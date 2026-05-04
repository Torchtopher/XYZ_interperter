from sys import argv
from os.path import isfile

from xyz.tokenizer import tokenize
from xyz.parser import parse
from xyz.error import Error

from xyz.parser.TokenIterator import TokenIterator


def main():
    if len(argv) < 2:
        print("No XYZ source file provided!")
    elif not isfile(argv[1]):
        print("File %s does not exist!" % argv[1])
    else:
        with open(argv[1], "r") as file:
            print("## IMPLEMENTATION STATUS - 2/3 (WIP)")
            print("## PRINTING PARSER OUTPUT")
            print()
            result = tokenize(file)
            if isinstance(result, Error):
                result.print()
            else:
                tree = parse(file, TokenIterator(result))
                if isinstance(tree, Error):
                    tree.print()
                else:
                    print("\nResult from parsing: \n")
                    print(tree)
            file.close()


if __name__ == "__main__":
    main()

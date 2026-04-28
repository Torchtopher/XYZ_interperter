from sys import argv
from os.path import isfile

from xyz.tokenizer import tokenize


def main():
    if len(argv) < 2:
        print("No XYZ source file provided!")
    elif not isfile(argv[1]):
        print("File %s does not exist!" % argv[1])
    else:
        with open(argv[1], "r") as file:
            print("## IMPLEMENTATION STATUS - 1/3 (WIP)")
            print("## PRINTING TOKENIZER OUTPUT")
            print()
            print(tokenize(file))
            file.close()


if __name__ == "__main__":
    main()

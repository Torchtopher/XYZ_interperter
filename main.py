from sys import argv
from os.path import isfile

from xyz.tokenizer import tokenize
from xyz.tokenizer.error import Error


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
            result = tokenize(file)
            if isinstance(result, Error):
                result.print()
            else:
                print(result)
            file.close()


if __name__ == "__main__":
    main()

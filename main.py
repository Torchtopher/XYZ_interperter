from sys import argv
from os.path import isfile


def main():
    if len(argv) < 2:
        print("No XYZ source file provided!")
    elif not isfile(argv[1]):
        print("File %s does not exist!" % argv[1])
    else:
        with open(argv[1], "r") as file:
            chunk = file.read()
            print("## IMPLEMENTATION STATUS - 0/3")
            print("## PRINTING CHUNK AS-IS")
            print()
            print(chunk)
            file.close()


if __name__ == "__main__":
    main()

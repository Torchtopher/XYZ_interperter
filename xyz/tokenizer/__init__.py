from xyz.tokenizer.tokens import Token, TokenType


def peek(file) -> str:
    pos: int = file.tell()
    nextchar: str = file.read(1)
    file.seek(pos)
    return nextchar


def tokenize(file) -> list[Token] | None:
    tokens: list[Token] = []
    start: int = 0
    while True:
        char: str = file.read(1)
        match char:
            case '':
                tokens.append((TokenType.EOF, (start, start+1), None))
                return tokens
            case _ if char.isspace():
                start += 1
            case _ if char.isalpha() or char == "_":
                ident: str = char
                end: int = start + 1
                while True:
                    nextchar: str = peek(file)
                    if nextchar.isalnum() or nextchar == "_":
                        ident += file.read(1)
                        end += 1
                    else:
                        break
                tokens.append((TokenType.IDENT, (start, end), ident))
                start = end
            case '-':
                if peek(file) == '-':
                    # handle comments
                    start += 2
                    while file.read(1) != "\n":
                        start += 1
                else:
                    tokens.append(
                        (TokenType.OP_MINUS, (start, start + 1), None))
                    start += 1
            case _:
                print("Bad token @ char %s!" % start)
                return None
    return tokens

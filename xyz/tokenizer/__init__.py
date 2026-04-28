from xyz.tokenizer.tokens import Token, TokenType


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
                    pos: int = file.tell()
                    nextchar: str = file.read(1)
                    if nextchar.isalnum() or nextchar == "_":
                        ident += nextchar
                        end += 1
                    else:
                        file.seek(pos)
                        break
                tokens.append((TokenType.IDENT, (start, end, ident)))
                start = end
            case _:
                print("Bad token @ char %s!" % start)
                return None
    return tokens

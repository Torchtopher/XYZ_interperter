from xyz.tokenizer.tokens import Token, TokenType


def peek(file) -> str:
    pos: int = file.tell()
    nextchar: str = file.read(1)
    file.seek(pos)
    return nextchar


def tokenize(file) -> list[Token] | None:
    tokens: list[Token] = []
    start: int = 0

    def report(token: Token):
        tokens.append(token)
        nonlocal start
        start = token[1][1]
    while True:
        char: str = file.read(1)
        match char:
            case '':
                report((TokenType.EOF, (start, start+1), None))
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
                report((TokenType.IDENT, (start, end), ident))
            case _ if char.isdecimal():
                report(tokenize_number(file, start, char))
            case '.':
                nextchar: str = peek(file)
                if nextchar.isdecimal():
                    report(tokenize_number(file, start, char))
                elif nextchar == '.':
                    file.read(1)
                    report(((TokenType.OP_CONCAT, (start, start+2), None)))
                else:
                    report((TokenType.DOT, (start, start+1), None))
                    start += 1
            case "'" | '"':
                report(tokenize_string(file, start, char))
            case '-':
                if peek(file) == '-':
                    # handle comments
                    start += 2
                    while file.read(1) != "\n":
                        start += 1
                else:
                    report((TokenType.OP_MINUS, (start, start + 1), None))
            case _:
                print("Bad token @ char %s! (%s)" % (start, char))
                return None
    return tokens


def tokenize_number(file, start, char) -> Token:
    frac: bool = char == '.'
    final: str = char
    end: int = start + 1
    while True:
        nextchar: str = peek(file)
        if not frac and nextchar == '.':
            frac = True
            final += file.read(1)
            end += 1
        elif nextchar.isdecimal():
            final += file.read(1)
            end += 1
        else:
            break
    return (TokenType.FLOAT if frac else TokenType.INT, (start, end), final)


def tokenize_string(file, start, char) -> Token:
    final: str = ""
    escape: bool = False
    end: int = start+1
    skipwhite: bool = False
    while True:
        nextchar: str = file.read(1)
        end += 1
        if skipwhite:
            if not nextchar.isspace():
                skipwhite = False
        elif escape:
            escape = False
            match nextchar:
                case 'a':
                    final += '\a'
                case 'b':
                    final += '\b'
                case 'f':
                    final += '\f'
                case 'n' | '\n':
                    final += '\n'
                case 'r':
                    final += '\r'
                case 't':
                    final += '\t'
                case 'v':
                    final += '\v'
                case '\\':
                    final += '\\'
                case '"':
                    final += '"'
                case "'":
                    final += "'"
                case 'z':
                    skipwhite = True
                # todo?: \xXX, \ddd, \u{XXX}
        elif nextchar == char:
            break
        elif nextchar == '\\':
            escape = True
        else:
            final += nextchar
    return (TokenType.STRING, (start, end), final)

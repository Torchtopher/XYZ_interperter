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
            case _ if char.isdecimal():
                num: tuple[int, Token] = tokenize_number(file, start, char)
                start = num[0]
                tokens.append(num[1])
            case '.':
                nextchar: str = peek(file)
                if nextchar.isdecimal():
                    num: tuple[int, Token] = tokenize_number(file, start, char)
                    start = num[0]
                    tokens.append(num[1])
                elif nextchar == '.':
                    file.read(1)
                    tokens.append(
                        (TokenType.OP_CONCAT, (start, start+2), None))
                    start += 2
                else:
                    tokens.append((TokenType.DOT, (start, start+1), None))
                    start += 1
            case "'" | '"':
                string: tuple[int, Token] = tokenize_string(file, start, char)
                start = string[0]
                tokens.append(string[1])
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
                print("Bad token @ char %s! (%s)" % (start, char))
                return None
    return tokens


def tokenize_number(file, start, char) -> tuple[int, Token]:
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
    return (end,
            (TokenType.FLOAT if frac else TokenType.INT, (start, end), final))


def tokenize_string(file, start, char) -> tuple[int, Token]:
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
    return (end, (TokenType.STRING, (start, end), final))

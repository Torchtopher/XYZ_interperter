from xyz.tokenizer.tokens import Token, TokenType, keywords


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
                report(tokenize_ident(file, start, char))
            case _ if char.isdecimal():
                report(tokenize_number(file, start, char))
            case '.':
                nextchar: str = peek(file)
                if nextchar.isdecimal():
                    report(tokenize_number(file, start, char))
                elif nextchar == '.':
                    file.read(1)
                    if peek(file) == '.':
                        file.read(1)
                        report((TokenType.ELLIPSIS, (start, start+3), None))
                    else:
                        report(((TokenType.OP_CONCAT, (start, start+2), None)))
                else:
                    report((TokenType.DOT, (start, start+1), None))
                    start += 1
            case "'" | '"':
                report(tokenize_string(file, start, char))
            case ';':
                report((TokenType.SEMICOLON, (start, start+1), None))
            case ',':
                report((TokenType.COMMA, (start, start+1), None))
            case '=':
                if peek(file) == '=':
                    file.read(1)
                    report((TokenType.OP_EQUAL, (start, start+2), None))
                else:
                    report((TokenType.SET, (start, start+1), None))
            case ':':
                report((TokenType.COLON, (start, start+1), None))
            case '(':
                report((TokenType.PAREN_OPEN, (start, start+1), None))
            case ')':
                report((TokenType.PAREN_CLOSE, (start, start+1), None))
            case '[':
                report((TokenType.BRACKET_OPEN, (start, start+1), None))
            case ']':
                report((TokenType.BRACKET_CLOSE, (start, start+1), None))
            case '{':
                report((TokenType.BRACE_OPEN, (start, start+1), None))
            case '}':
                report((TokenType.BRACE_CLOSE, (start, start+1), None))
            case '+':
                report((TokenType.OP_PLUS, (start, start+1), None))
            case '-':
                if peek(file) == '-':
                    # handle comments
                    start += 2
                    while file.read(1) != "\n":
                        start += 1
                else:
                    report((TokenType.OP_MINUS, (start, start + 1), None))
            case '*':
                if peek(file) == '*':
                    file.read(1)
                    report((TokenType.OP_EXP, (start, start+2), None))
                else:
                    report((TokenType.OP_MUL, (start, start+1), None))
            case '/':
                if peek(file) == '/':
                    file.read(1)
                    report((TokenType.OP_FLOORDIV, (start, start+2), None))
                else:
                    report((TokenType.OP_DIV, (start, start+1), None))
            case '%':
                report((TokenType.OP_MOD, (start, start+1), None))
            case '&':
                report((TokenType.OP_AND, (start, start+1), None))
            case '^':
                report((TokenType.OP_XOR, (start, start+1), None))
            case '|':
                report((TokenType.OP_OR, (start, start+1), None))
            case '<':
                nextchar: str = peek(file)
                if nextchar == '<':
                    report((TokenType.OP_LSHIFT, (start, start+2), None))
                elif nextchar == '=':
                    report((TokenType.OP_LEQ, (start, start+2), None))
                else:
                    report((TokenType.OP_LESS, (start, start+1), None))
            case '>':
                nextchar: str = peek(file)
                if nextchar == '>':
                    report((TokenType.OP_RSHIFT, (start, start+2), None))
                elif nextchar == '=':
                    report((TokenType.OP_GEQ, (start, start+2), None))
                else:
                    report((TokenType.OP_GREATER, (start, start+1), None))
            case '#':
                report((TokenType.OP_SIZE, (start, start+1), None))
            case '!':
                if peek(file) == '=':
                    report((TokenType.OP_NEQ, (start, start+2), None))
                else:
                    report((TokenType.OP_NOT, (start, start+1), None))
            case _:
                print("Bad token @ char %s! (%s)" % (start, char))
                return None
    return tokens


def tokenize_ident(file, start, char) -> Token:
    ident: str = char
    end: int = start + 1
    while True:
        nextchar: str = peek(file)
        if nextchar.isalnum() or nextchar == "_":
            ident += file.read(1)
            end += 1
        else:
            break
    if ident in keywords.keys():
        return (keywords[ident], (start, end), None)
    else:
        return (TokenType.IDENT, (start, end), ident)


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

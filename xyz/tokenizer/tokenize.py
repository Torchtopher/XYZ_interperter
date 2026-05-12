from xyz.tokenizer.tokens import Token, TokenType, keywords
from xyz.error import Error, Span
from xyz.tokenizer.error import (
    InvalidTokenError, InvalidEscapeError,
    StringNewlineError, UnexpectedEndError)
from types import GeneratorType


def peek(file) -> str:
    pos: int = file.tell()
    nextchar: str = file.read(1)
    file.seek(pos)
    return nextchar


def tokenize(file) -> list[Token] | Error:
    tokens: list[Token] = []
    line: int = 1
    col: int = 1

    def span(width: int) -> Span:
        return ((line, col), (line, col+width))

    def tokenize_iter(file) -> GeneratorType[Token | Error]:
        nonlocal line, col

        while True:
            char: str = file.read(1)
            match char:
                case '':
                    yield Token(TokenType.EOF, span(1), None)
                    return
                case _ if char.isspace():
                    if char == "\n":
                        line += 1
                        col = 1
                    else:
                        col += 1
                case _ if char.isalpha() or char == "_":
                    yield tokenize_ident(file, line, col, char)
                case _ if char.isdecimal():
                    yield tokenize_number(file, line, col, char)
                case '.':
                    nextchar: str = peek(file)
                    if nextchar.isdecimal():
                        yield tokenize_number(file, line, col, char)
                    elif nextchar == '.':
                        file.read(1)
                        if peek(file) == '.':
                            file.read(1)
                            yield Token(TokenType.ELLIPSIS, span(3), None)
                        else:
                            yield Token(TokenType.OP_CONCAT, span(2), None)
                    else:
                        yield Token(TokenType.DOT, span(1), None)
                case "'" | '"':
                    yield tokenize_string(file, line, col, char)
                case ';':
                    yield Token(TokenType.SEMICOLON, span(1), None)
                case ',':
                    yield Token(TokenType.COMMA, span(1), None)
                case '=':
                    if peek(file) == '=':
                        file.read(1)
                        yield Token(TokenType.OP_EQUAL, span(2), None)
                    else:
                        yield Token(TokenType.SET, span(1), None)
                case ':':
                    yield Token(TokenType.COLON, span(1), None)
                case '(':
                    yield Token(TokenType.PAREN_OPEN, span(1), None)
                case ')':
                    yield Token(TokenType.PAREN_CLOSE, span(1), None)
                case '[':
                    yield Token(TokenType.BRACKET_OPEN, span(1), None)
                case ']':
                    yield Token(TokenType.BRACKET_CLOSE, span(1), None)
                case '{':
                    yield Token(TokenType.BRACE_OPEN, span(1), None)
                case '}':
                    yield Token(TokenType.BRACE_CLOSE, span(1), None)
                case '+':
                    yield Token(TokenType.OP_PLUS, span(1), None)
                case '-':
                    if peek(file) == '-':
                        # handle comments
                        while file.read(1) != "\n":
                            pass
                        line += 1
                        col = 1
                    else:
                        yield Token(TokenType.OP_MINUS, span(1), None)
                case '*':
                    if peek(file) == '*':
                        file.read(1)
                        yield Token(TokenType.OP_EXP, span(2), None)
                    else:
                        yield Token(TokenType.OP_MUL, span(1), None)
                case '/':
                    if peek(file) == '/':
                        file.read(1)
                        yield Token(TokenType.OP_FLOORDIV, span(2), None)
                    else:
                        yield Token(TokenType.OP_DIV, span(1), None)
                case '%':
                    yield Token(TokenType.OP_MOD, span(1), None)
                case '&':
                    yield Token(TokenType.OP_AND, span(1), None)
                case '^':
                    yield Token(TokenType.OP_XOR, span(1), None)
                case '|':
                    yield Token(TokenType.OP_OR, span(1), None)
                case '<':
                    nextchar: str = peek(file)
                    if nextchar == '<':
                        file.read(1)
                        yield Token(TokenType.OP_LSHIFT, span(2), None)
                    elif nextchar == '=':
                        file.read(1)
                        yield Token(TokenType.OP_LEQ, span(2), None)
                    else:
                        yield Token(TokenType.OP_LESS, span(1), None)
                case '>':
                    nextchar: str = peek(file)
                    if nextchar == '>':
                        file.read(1)
                        yield Token(TokenType.OP_RSHIFT, span(2), None)
                    elif nextchar == '=':
                        file.read(1)
                        yield Token(TokenType.OP_GEQ, span(2), None)
                    else:
                        yield Token(TokenType.OP_GREATER, span(1), None)
                case '#':
                    yield Token(TokenType.OP_SIZE, span(1), None)
                case '!':
                    if peek(file) == '=':
                        file.read(1)
                        yield Token(TokenType.OP_NEQ, span(2), None)
                    else:
                        yield Token(TokenType.OP_NOT, span(1), None)
                case _:
                    yield InvalidTokenError(span(1), file, char)
    for token in tokenize_iter(file):
        if isinstance(token, Error):
            return token
        tokens.append(token)
        line = token[1][1][0]
        col = token[1][1][1]
    return tokens


def tokenize_ident(file, line, col, char) -> Token:
    ident: str = char
    end: int = col + 1
    while True:
        nextchar: str = peek(file)
        if nextchar.isalnum() or nextchar == "_":
            ident += file.read(1)
            end += 1
        else:
            break
    if ident in keywords.keys():
        return Token(keywords[ident], ((line, col), (line, end)), None)
    else:
        return Token(TokenType.IDENT, ((line, col), (line, end)), ident)


def tokenize_number(file, line, col, char) -> Token:
    frac: bool = char == '.'
    final: str = char
    end: int = col + 1
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
    return Token(TokenType.FLOAT if frac else TokenType.INT, ((line, col), (line, end)), final)


def tokenize_string(file, line, col, char) -> Token | Error:
    final: str = ""
    escape: bool = False
    end_line: int = line
    end_col: int = col+1
    skipwhite: bool = False
    while True:
        nextchar: str = file.read(1)
        if nextchar == '':
            return UnexpectedEndError(((line, col), (end_line, end_col+1)), file)
        end_col += 1
        if skipwhite:
            if not nextchar.isspace():
                skipwhite = False
            elif nextchar == "\n":
                old_lc = (end_line, end_col-1)
                return StringNewlineError((old_lc, (end_line + 1, 2)), file)

        elif escape:
            escape = False
            match nextchar:
                case 'a':
                    final += '\a'
                case 'b':
                    final += '\b'
                case 'f':
                    final += '\f'
                case 'n':
                    final += '\n'
                case '\n':
                    final += '\n'
                    end_line += 1
                    end_col = 1
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
                case _:
                    return InvalidEscapeError(((end_line, end_col-2), (end_line, end_col)), file, nextchar)
        elif nextchar == char:
            break
        elif nextchar == '\\':
            escape = True
        elif nextchar == '\n':
            return StringNewlineError(((end_line, end_col-1), (end_line + 1, 2)), file)
        else:
            final += nextchar
    return Token(TokenType.STRING, ((line, col), (end_line, end_col)), final)

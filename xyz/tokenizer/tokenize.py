from xyz.tokenizer.tokens import Token, TokenType, keywords
from xyz.error import Error
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
    start: int = 0

    def tokenize_iter(file) -> GeneratorType[Token | Error]:
        nonlocal start

        while True:
            char: str = file.read(1)
            match char:
                case '':
                    yield Token(TokenType.EOF, (start, start+1), None)
                    return
                case _ if char.isspace():
                    start += 1
                case _ if char.isalpha() or char == "_":
                    yield tokenize_ident(file, start, char)
                case _ if char.isdecimal():
                    yield tokenize_number(file, start, char)
                case '.':
                    nextchar: str = peek(file)
                    if nextchar.isdecimal():
                        yield tokenize_number(file, start, char)
                    elif nextchar == '.':
                        file.read(1)
                        if peek(file) == '.':
                            file.read(1)
                            yield Token(TokenType.ELLIPSIS, (start, start+3), None)
                        else:
                            yield Token(TokenType.OP_CONCAT, (start, start+2), None)
                    else:
                        yield Token(TokenType.DOT, (start, start+1), None)
                        start += 1
                case "'" | '"':
                    yield tokenize_string(file, start, char)
                case ';':
                    yield Token(TokenType.SEMICOLON, (start, start+1), None)
                case ',':
                    yield Token(TokenType.COMMA, (start, start+1), None)
                case '=':
                    if peek(file) == '=':
                        file.read(1)
                        yield Token(TokenType.OP_EQUAL, (start, start+2), None)
                    else:
                        yield Token(TokenType.SET, (start, start+1), None)
                case ':':
                    yield Token(TokenType.COLON, (start, start+1), None)
                case '(':
                    yield Token(TokenType.PAREN_OPEN, (start, start+1), None)
                case ')':
                    yield Token(TokenType.PAREN_CLOSE, (start, start+1), None)
                case '[':
                    yield Token(TokenType.BRACKET_OPEN, (start, start+1), None)
                case ']':
                    yield Token(TokenType.BRACKET_CLOSE, (start, start+1), None)
                case '{':
                    yield Token(TokenType.BRACE_OPEN, (start, start+1), None)
                case '}':
                    yield Token(TokenType.BRACE_CLOSE, (start, start+1), None)
                case '+':
                    yield Token(TokenType.OP_PLUS, (start, start+1), None)
                case '-':
                    if peek(file) == '-':
                        # handle comments
                        start += 2
                        while file.read(1) != "\n":
                            start += 1
                    else:
                        yield Token(TokenType.OP_MINUS, (start, start + 1), None)
                case '*':
                    if peek(file) == '*':
                        file.read(1)
                        yield Token(TokenType.OP_EXP, (start, start+2), None)
                    else:
                        yield Token(TokenType.OP_MUL, (start, start+1), None)
                case '/':
                    if peek(file) == '/':
                        file.read(1)
                        yield Token(TokenType.OP_FLOORDIV, (start, start+2), None)
                    else:
                        yield Token(TokenType.OP_DIV, (start, start+1), None)
                case '%':
                    yield Token(TokenType.OP_MOD, (start, start+1), None)
                case '&':
                    yield Token(TokenType.OP_AND, (start, start+1), None)
                case '^':
                    yield Token(TokenType.OP_XOR, (start, start+1), None)
                case '|':
                    yield Token(TokenType.OP_OR, (start, start+1), None)
                case '<':
                    nextchar: str = peek(file)
                    if nextchar == '<':
                        file.read(1)
                        yield Token(TokenType.OP_LSHIFT, (start, start+2), None)
                    elif nextchar == '=':
                        file.read(1)
                        yield Token(TokenType.OP_LEQ, (start, start+2), None)
                    else:
                        yield Token(TokenType.OP_LESS, (start, start+1), None)
                case '>':
                    nextchar: str = peek(file)
                    if nextchar == '>':
                        file.read(1)
                        yield Token(TokenType.OP_RSHIFT, (start, start+2), None)
                    elif nextchar == '=':
                        file.read(1)
                        yield Token(TokenType.OP_GEQ, (start, start+2), None)
                    else:
                        yield Token(TokenType.OP_GREATER, (start, start+1), None)
                case '#':
                    yield Token(TokenType.OP_SIZE, (start, start+1), None)
                case '!':
                    if peek(file) == '=':
                        file.read(1)
                        yield Token(TokenType.OP_NEQ, (start, start+2), None)
                    else:
                        yield Token(TokenType.OP_NOT, (start, start+1), None)
                case _:
                    yield InvalidTokenError((start, start+1), file, char)
    for token in tokenize_iter(file):
        if isinstance(token, Error):
            return token
        tokens.append(token)
        start = token[1][1]
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
        return Token(keywords[ident], (start, end), None)
    else:
        return Token(TokenType.IDENT, (start, end), ident)


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
    return Token(TokenType.FLOAT if frac else TokenType.INT, (start, end), final)


def tokenize_string(file, start, char) -> Token | Error:
    final: str = ""
    escape: bool = False
    end: int = start+1
    skipwhite: bool = False
    while True:
        nextchar: str = file.read(1)
        if nextchar == '':
            return UnexpectedEndError((end, end+1), file)
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
                case _:
                    return InvalidEscapeError((end-2, end), file, nextchar)
        elif nextchar == char:
            break
        elif nextchar == '\\':
            escape = True
        elif nextchar == '\n':
            return StringNewlineError((end-2, end), file)
        else:
            final += nextchar
    return Token(TokenType.STRING, (start, end), final)

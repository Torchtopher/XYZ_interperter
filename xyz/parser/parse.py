from io import StringIO
from typing import Callable
from xyz.parser.error import WrongTokenError, NoGrammarMatchError
from xyz.tokenizer import TokenType as TT
import xyz.parser.ast as AST
from xyz.error import Error
from xyz.parser.token_iterator import TokenIterator

# For simplicity, the parser uses the python Exception system instead of an error-as-value system.
# These are converted back to errors-as-values at the top of the parser call stack.

BINARY_TOKENS_TO_AST = {TT.OP_MINUS: AST.BinExpType.SUB, 
                        TT.OP_PLUS: AST.BinExpType.ADD,
                        TT.OP_MUL: AST.BinExpType.MUL,
                        TT.OP_FLOORDIV: AST.BinExpType.FLOORDIV,
                        TT.OP_DIV: AST.BinExpType.DIV,
                        TT.OP_MOD: AST.BinExpType.MOD,
                        TT.OP_EXP: AST.BinExpType.EXP,
                        TT.OP_AND: AST.BinExpType.BIT_AND,
                        TT.OP_XOR: AST.BinExpType.BIT_XOR,
                        TT.OP_OR: AST.BinExpType.BIT_OR,
                        TT.OP_LSHIFT: AST.BinExpType.LSHIFT,
                        TT.OP_RSHIFT: AST.BinExpType.RSHIFT,
                        TT.OP_CONCAT: AST.BinExpType.CONCAT,
                        TT.OP_LESS: AST.BinExpType.LESS,
                        TT.OP_LEQ: AST.BinExpType.LEQ,
                        TT.OP_GREATER: AST.BinExpType.GREATER,
                        TT.OP_GEQ: AST.BinExpType.GEQ,
                        TT.OP_EQUAL: AST.BinExpType.EQUAL,
                        TT.OP_NEQ: AST.BinExpType.NEQ,
                        TT.KEYWORD_AND: AST.BinExpType.AND,
                        TT.KEYWORD_OR: AST.BinExpType.OR}

UNARY_TOKENS_TO_AST = {TT.OP_SIZE: AST.UnExpType.SIZE, 
                       TT.OP_NOT: AST.UnExpType.NOT, 
                       TT.KEYWORD_NOT: AST.UnExpType.NOT,
                       TT.OP_MINUS: AST.UnExpType.NEG,
                       }

def parse(source: StringIO, tokens: TokenIterator) -> AST.File | Error:

    # ---

    # recursion hierarchy (bottom is highest priority)

    # Precedence definition (top down)
    # or
    # and
    # < > <= >= != ==
    # |
    # ^
    # &
    # << >>
    # ..
    # + -
    # * / // %  :parse_mul_div()
    # unary: ! not # -  :parse_unary()
    # **  :parse_power()
    # idents, literals :parse_primary()

    def parse_expression(tokens: TokenIterator) -> AST.Expression:
        return parse_or(tokens)

    # helper function for repetitve binary ops
    def parse_general_binary_op(
        tokens: TokenIterator,
        operators: list[TT],
        next_func: Callable[[TokenIterator], AST.Expression],
    ) -> AST.Expression:
        # next_func is one down on the ladder
        exp = next_func(tokens)

        while (tokens.match(operators)):
            t = tokens.prev()
            rhs: AST.Expression = next_func(tokens)
            exp = AST.BinaryExpression(BINARY_TOKENS_TO_AST[t.type], exp, rhs)

        return exp

    def parse_or(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.KEYWORD_OR], parse_and)

    def parse_and(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.KEYWORD_AND], parse_comparison)

    def parse_comparison(tokens: TokenIterator) -> AST.Expression:
        operators = [TT.OP_LESS,
                     TT.OP_LEQ,
                     TT.OP_GREATER,
                     TT.OP_GEQ,
                     TT.OP_EQUAL,
                     TT.OP_NEQ]
        return parse_general_binary_op(tokens, operators, parse_bit_or)

    def parse_bit_or(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_OR], parse_bit_xor)

    def parse_bit_xor(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_XOR], parse_bit_and)

    def parse_bit_and(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_AND], parse_shift)

    def parse_shift(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_LSHIFT, TT.OP_RSHIFT], parse_concat)

    def parse_concat(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_CONCAT], parse_add_sub)
    
    def parse_add_sub(tokens: TokenIterator) -> AST.Expression: 
        return parse_general_binary_op(tokens, [TT.OP_MINUS, TT.OP_PLUS], parse_mul_div)


    def parse_mul_div(tokens: TokenIterator):
        operators = [TT.OP_MUL,
                     TT.OP_DIV,
                     TT.OP_FLOORDIV,
                     TT.OP_MOD]
        return parse_general_binary_op(tokens, operators, parse_unary)

    def parse_unary(tokens: TokenIterator) -> AST.Expression:

        while (tokens.match([TT.OP_MINUS,
                             TT.OP_NOT,
                             TT.KEYWORD_NOT,
                             TT.OP_SIZE])):
            t = tokens.prev()
            rhs: AST.Expression = parse_unary(tokens)
            return AST.UnaryExpression(UNARY_TOKENS_TO_AST[t.type], rhs)
        
        exp = parse_power(tokens)

        return exp

    def parse_power(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_EXP], parse_primary)

    def parse_primary(tokens: TokenIterator) -> AST.Expression: 
        if (tokens.match(TT.INT)):
            t = tokens.prev()
            return AST.LitInt(int(t.name))
      
        if (tokens.match(TT.FLOAT)):
            t = tokens.prev()
            return AST.LitFloat(float(t.name))

        if (tokens.match(TT.STRING)):
            t = tokens.prev()
            return AST.LitString(t.name)

        if (tokens.match(TT.KEYWORD_TRUE)):
            return AST.LitTrue(True)
      
        if (tokens.match(TT.KEYWORD_FALSE)):
            return AST.LitFalse(False)

        if (tokens.match(TT.KEYWORD_NIL)):
            return AST.LitNil(None)
        
        if (tokens.match(TT.IDENT)):
            name = tokens.prev().name
            return parse_prefixexp_actions(AST.Var(name), tokens)
        
        if (tokens.match(TT.PAREN_OPEN)):
            exp = parse_expression(tokens)
            tokens.expect(TT.PAREN_CLOSE, source)
            return parse_prefixexp_actions(exp, tokens)

        if (tokens.match(TT.BRACE_OPEN)):
            table = parse_table(tokens)
            tokens.expect(TT.BRACE_CLOSE, source)
            return table

        if (tokens.match(TT.KEYWORD_FUNCTION)):
            return parse_lambda(tokens)


        # expected more than just ident but close enough
        raise NoGrammarMatchError(tokens.curr().span, source, "expression")

    def parse_prefixexp_actions(prefixexp: AST.Expression, tokens: TokenIterator) -> AST.Expression:
        final = prefixexp
        while (tokens.match([TT.DOT, TT.BRACKET_OPEN, TT.COLON, TT.PAREN_OPEN])):
            t = tokens.prev()
            match (t.type):
                case TT.DOT:
                    next_accessor = tokens.expect(TT.IDENT, source).name
                    assert next_accessor != None
                    final = AST.Access(final, AST.LitString(next_accessor))
                case TT.BRACKET_OPEN:
                    final = AST.Access(final, parse_expression(tokens))
                    tokens.expect(TT.BRACKET_CLOSE, source)
                case TT.COLON:
                    next_accessor = tokens.expect(TT.IDENT, source).name
                    assert next_accessor != None
                    final = AST.Access(final, AST.LitString(next_accessor))
                    tokens.expect(TT.PAREN_OPEN, source)
                    return parse_call(True, final, tokens)
                case TT.PAREN_OPEN:
                    if not isinstance(final, AST.Access): final = AST.Access(final, None)
                    return parse_call(False, final, tokens)
        return final

    def parse_call(method: bool, access: AST.Access, tokens: TokenIterator) -> AST.Expression:
        args: list[AST.Expression] = []
        stop: bool = False
        while not stop and not tokens.match(TT.PAREN_CLOSE):
            args.append(parse_expression(tokens))
            if not tokens.match(TT.COMMA):
                stop = True
        tokens.expect(TT.PAREN_CLOSE, source)
        return parse_prefixexp_actions(AST.FunctionCall(method, access, args), tokens)

    # todo! fields
    def parse_table(tokens: TokenIterator) -> AST.LitTable:
        return AST.LitTable([])

    def parse_lambda(tokens: TokenIterator) -> AST.Lambda:
        tokens.expect(TT.PAREN_OPEN, source)
        args: list[str] = []
        extra: str | None = None
        stop: bool = False
        while not stop and tokens.expect([TT.IDENT, TT.ELLIPSIS], source):
            t = tokens.prev()
            match (t.type):
                case TT.IDENT:
                    args.append(t.name)
                    if not tokens.match(TT.COMMA):
                        stop = True
                case TT.ELLIPSIS:
                    extra = tokens.expect(TT.IDENT, source).name
                    stop = True
        tokens.expect(TT.PAREN_CLOSE, source)
        return AST.Lambda(args, extra, parse_block(TT.KEYWORD_END, tokens))

    # todo! statements
    def parse_block(until: TT, tokens: TokenIterator) -> AST.Block:
        block = AST.Block([], parse_expression(tokens))
        tokens.expect(until, source)
        return block

    print(tokens)

    try:
        file: AST.File = parse_block(TT.EOF, tokens)
    except Error as error: return error
    
    return file

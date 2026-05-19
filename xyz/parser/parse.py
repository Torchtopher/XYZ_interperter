"""
The main logic of the parser.
"""

from typing import Callable
from xyz.parser.error import WrongTokenError, NoGrammarMatchError
from xyz.tokenizer import TokenType as TT
import xyz.parser.ast as AST
from xyz.error import Error, XYZSource
from xyz.parser.token_iterator import TokenIterator

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

def parse(source: XYZSource, tokens: TokenIterator) -> AST.File | Error:
    """
    Parses a token stream into an AST.
    
    Args:
      source:
        An XYZSource, for error reporting.
      tokens:
        A TokenIterator from the list of tokens given by the tokenizer.
    """

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

    # helper function for repetitive binary ops
    def parse_general_binary_op(
        tokens: TokenIterator,
        operators: list[TT],
        next_func: Callable[[TokenIterator], AST.Expression],
    ) -> AST.Expression:
        # next_func is one down on the ladder
        start_pos = tokens.curr().span[0]
        exp = next_func(tokens)

        while (tokens.match(operators)):
            t = tokens.prev()
            rhs: AST.Expression = next_func(tokens)
            exp = AST.BinaryExpression((start_pos, tokens.prev().span[1]), BINARY_TOKENS_TO_AST[t.type], exp, rhs)

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

        if (tokens.match([TT.OP_MINUS,
                             TT.OP_NOT,
                             TT.KEYWORD_NOT,
                             TT.OP_SIZE])):
            t = tokens.prev()
            rhs: AST.Expression = parse_unary(tokens)
            return AST.UnaryExpression((t.span[0], tokens.prev().span[1]), UNARY_TOKENS_TO_AST[t.type], rhs)
        
        exp = parse_power(tokens)

        return exp

    def parse_power(tokens: TokenIterator) -> AST.Expression:
        return parse_general_binary_op(tokens, [TT.OP_EXP], parse_primary)

    def parse_primary(tokens: TokenIterator) -> AST.Expression: 
        if (tokens.match(TT.INT)):
            t = tokens.prev()
            assert isinstance(t.name, str)
            return AST.LitInt(t.span, int(t.name))
      
        if (tokens.match(TT.FLOAT)):
            t = tokens.prev()
            assert isinstance(t.name, str)
            return AST.LitFloat(t.span, float(t.name))

        if (tokens.match(TT.STRING)):
            t = tokens.prev()
            assert isinstance(t.name, str)
            return AST.LitString(t.span, t.name)

        if (tokens.match(TT.KEYWORD_TRUE)):
            return AST.LitTrue(tokens.prev().span, True)
      
        if (tokens.match(TT.KEYWORD_FALSE)):
            return AST.LitFalse(tokens.prev().span, False)

        if (tokens.match(TT.KEYWORD_NIL)):
            return AST.LitNil(tokens.prev().span, None)
        
        if (tokens.match(TT.IDENT)):
            t = tokens.prev()
            assert isinstance(t.name, str)
            return parse_prefixexp_actions(AST.Var(t.span, t.name), tokens)
        
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

        raise NoGrammarMatchError(tokens.curr().span, source, "expression")

    def parse_prefixexp_actions(prefixexp: AST.Expression, tokens: TokenIterator) -> AST.Expression:
        # after a variable name, function call, or grouped expression (a "prefixexp"), more calls and accessors can be chained.
        final = prefixexp
        while (tokens.match([TT.DOT, TT.BRACKET_OPEN, TT.COLON, TT.PAREN_OPEN])):
            t = tokens.prev()
            match (t.type):
                case TT.DOT:
                    next_accessor = tokens.expect(TT.IDENT, source)
                    assert next_accessor.name != None
                    final = AST.Access((final.span[0], tokens.prev().span[1]), final, AST.LitString(next_accessor.span, next_accessor.name))
                case TT.BRACKET_OPEN:
                    next_accessor = parse_expression(tokens)
                    tokens.expect(TT.BRACKET_CLOSE, source)
                    final = AST.Access((final.span[0], tokens.prev().span[1]), final, next_accessor)
                case TT.COLON:
                    next_accessor = tokens.expect(TT.IDENT, source)
                    assert next_accessor.name != None
                    final = AST.Access((final.span[0], tokens.prev().span[1]), final, AST.LitString(next_accessor.span, next_accessor.name))
                    tokens.expect(TT.PAREN_OPEN, source)
                    return parse_call(True, final, tokens)
                case TT.PAREN_OPEN:
                    if not isinstance(final, AST.Access): final = AST.Access((final.span[0], tokens.prev(2).span[1]), final, None)
                    return parse_call(False, final, tokens)
        return final

    def parse_call(method: bool, access: AST.Access, tokens: TokenIterator) -> AST.Expression:
        args: list[AST.Expression] = []
        stop: bool = False
        while not stop and tokens.curr().type != TT.PAREN_CLOSE:
            args.append(parse_expression(tokens))
            if not tokens.match(TT.COMMA):
                stop = True
        tokens.expect(TT.PAREN_CLOSE, source)
        return parse_prefixexp_actions(AST.FunctionCall((access.span[0], tokens.prev().span[1]), method, access, args), tokens)

    def parse_table(tokens: TokenIterator) -> AST.LitTable:
        start = tokens.prev().span[0]
        fields: list[tuple[AST.Expression, AST.Expression]] = []
        index = 0 # important difference from lua: keyless values will be auto-indexed starting at *0*.
        stop: bool = False
        while not stop:
            t = tokens.next()
            expr: bool = False
            match (t.type):
                case TT.BRACKET_OPEN:
                    key = parse_expression(tokens)
                    tokens.expect(TT.BRACKET_CLOSE, source)
                    tokens.expect(TT.SET, source)
                    fields.append((key, parse_expression(tokens)))
                case TT.IDENT:
                    assert isinstance(t.name, str)
                    if (tokens.curr().type == TT.SET):
                        tokens.expect(TT.SET, source)
                        key = AST.LitString(t.span, t.name)
                        fields.append((key, parse_expression(tokens)))
                    else:
                        tokens.back()
                        expr = True
                case TT.BRACE_CLOSE:
                    tokens.back()
                    break
                case _:
                    tokens.back()
                    expr = True
            if expr:
                key = AST.LitInt(tokens.curr().span, index)
                index += 1
                fields.append((key, parse_expression(tokens)))
            if not tokens.match(TT.COMMA):
                stop = True
        return AST.LitTable((start, tokens.curr().span[1]), fields)

    def parse_lambda(tokens: TokenIterator, method: bool = False) -> AST.Lambda:
        start = tokens.prev().span[0]
        tokens.expect(TT.PAREN_OPEN, source)
        args: list[str] = ["self"] if method else []
        extra: str | None = None
        stop: bool = False
        while not stop and tokens.match([TT.IDENT, TT.ELLIPSIS]):
            t = tokens.prev()
            match (t.type):
                case TT.IDENT:
                    assert isinstance(t.name, str)
                    args.append(t.name)
                    if not tokens.match(TT.COMMA):
                        stop = True
                case TT.ELLIPSIS:
                    extra = tokens.expect(TT.IDENT, source).name
                    stop = True
        tokens.expect(TT.PAREN_CLOSE, source)
        block = parse_block(TT.KEYWORD_END, tokens)
        return AST.Lambda((start, tokens.prev().span[1]), args, extra, block)

    def parse_definition(tokens: TokenIterator, const: bool) -> AST.Definition:
        start = tokens.prev().span[0]
        ident = tokens.expect(TT.IDENT, source)
        assert isinstance(ident.name, str)
        var: list[AST.Var] = [AST.Var(ident.span, ident.name)]
        while tokens.match(TT.COMMA):
            ident = tokens.expect(TT.IDENT, source)
            assert isinstance(ident.name, str)
            var.append(AST.Var(ident.span, ident.name))
        tokens.expect(TT.SET, source)
        value: list[AST.Expression] = [parse_expression(tokens)]
        while tokens.match(TT.COMMA):
            value.append(parse_expression(tokens))
        return AST.Definition((start, tokens.prev().span[1]), const, var, value)

    def parse_block(until: TT | list[TT], tokens: TokenIterator) -> AST.Block:
        start_pos = tokens.curr().span[0]
        statements: list[AST.Statement] = []
        while not tokens.match(until):
            t = tokens.next()
            match (t.type):
                case TT.SEMICOLON:
                    pass # noop
                case TT.KEYWORD_LET:
                    statements.append(parse_definition(tokens, False))
                case TT.KEYWORD_CONST:
                    statements.append(parse_definition(tokens, True))
                case TT.KEYWORD_BREAK:
                    statements.append(AST.Break(t.span))
                case TT.KEYWORD_DO:
                    statements.append(parse_block(TT.KEYWORD_END, tokens))
                case TT.KEYWORD_WHILE:
                    expression: AST.Expression = parse_expression(tokens)
                    tokens.expect(TT.KEYWORD_DO, source)
                    block: AST.Block = parse_block(TT.KEYWORD_END, tokens)
                    statements.append(AST.WhileLoop((t.span[0], tokens.prev().span[1]), expression, block))
                case TT.KEYWORD_REPEAT:
                    block: AST.Block = parse_block(TT.KEYWORD_UNTIL, tokens)
                    expression: AST.Expression = parse_expression(tokens)
                    statements.append(AST.RepeatLoop((t.span[0], tokens.prev().span[1]), expression, block))
                case TT.KEYWORD_IF:
                    conditions: list[tuple[AST.Expression, AST.Block]] = []
                    else_block: AST.Block | None = None
                    cond = parse_expression(tokens)
                    tokens.expect(TT.KEYWORD_THEN, source)
                    conditions.append((cond, parse_block([TT.KEYWORD_ELSEIF, TT.KEYWORD_ELSE, TT.KEYWORD_END], tokens)))
                    while tokens.prev().type != TT.KEYWORD_END:
                        match tokens.prev().type:
                            case TT.KEYWORD_ELSEIF:
                                cond = parse_expression(tokens)
                                tokens.expect(TT.KEYWORD_THEN, source)
                                conditions.append((cond, parse_block([TT.KEYWORD_ELSEIF, TT.KEYWORD_ELSE, TT.KEYWORD_END], tokens)))
                            case TT.KEYWORD_ELSE:
                                else_block: AST.Block = parse_block(TT.KEYWORD_END, tokens)
                                #statements.append(AST.IfStatement((t.span[0], tokens.prev().span[1]), conditions, block))
                                break
                    statements.append(AST.IfStatement((t.span[0], tokens.prev().span[1]), conditions, else_block))
                case TT.KEYWORD_FOR:
                    ident = tokens.expect(TT.IDENT, source)
                    assert isinstance(ident.name, str)
                    tokens.expect(TT.KEYWORD_IN, source)
                    start = parse_expression(tokens)
                    tokens.expect(TT.COMMA, source)
                    end = parse_expression(tokens)
                    tokens.expect(TT.COMMA, source)
                    step = parse_expression(tokens)
                    tokens.expect(TT.KEYWORD_DO, source)
                    block: AST.Block = parse_block(TT.KEYWORD_END, tokens)
                    statements.append(AST.ForLoop((t.span[0], tokens.prev().span[1]), ident.name, start, end, step, block))
                case TT.KEYWORD_FUNCTION:
                    ident = tokens.expect(TT.IDENT, source)
                    assert isinstance(ident.name, str)
                    var: AST.Var | AST.Access = AST.Var(ident.span, ident.name)
                    method: bool = False
                    while tokens.match([TT.DOT, TT.COLON]):
                        match tokens.prev().type:
                            case TT.DOT:
                                next_accessor = tokens.expect(TT.IDENT, source)
                                assert next_accessor.name != None
                                var = AST.Access((var.span[0], tokens.prev().span[1]), var, AST.LitString(next_accessor.span, next_accessor.name))
                            case TT.COLON:
                                next_accessor = tokens.expect(TT.IDENT, source)
                                assert next_accessor.name != None
                                var = AST.Access((var.span[0], tokens.prev().span[1]), var, AST.LitString(next_accessor.span, next_accessor.name))
                                method = True
                                break
                    if isinstance(var, AST.Var):
                        function: AST.Lambda = parse_lambda(tokens)
                        statements.append(AST.Definition((t.span[0], tokens.prev().span[1]), True, [AST.Var(ident.span, ident.name)], [function]))
                    else:
                        function: AST.Lambda = parse_lambda(tokens, method)
                        statements.append(AST.SetStatement((t.span[0], tokens.prev().span[1]), [var], [function]))
                case TT.KEYWORD_RETURN:
                    ret = parse_expression(tokens)
                    tokens.expect(until, source)
                    return AST.Block((start_pos, tokens.prev().span[1]), statements, ret)
                case _:
                    start = tokens.back()
                    expr = parse_expression(tokens)
                    if isinstance(expr, AST.Var):
                        expr = AST.Access(expr.span, expr, None)
                    if isinstance(expr, AST.FunctionCall):
                        statements.append(expr)
                    elif isinstance(expr, AST.Access):
                        var: list[AST.Access] = [expr]
                        while tokens.match(TT.COMMA):
                            start = tokens.curr()
                            next_var = parse_expression(tokens)
                            if isinstance(next_var, AST.Var):
                                next_var = AST.Access(next_var.span, next_var, None)
                            if not isinstance(next_var, AST.Access):
                                raise NoGrammarMatchError((start.span[0], tokens.prev().span[1]), source, "variable or indexed expression")
                            var.append(next_var)
                        tokens.expect(TT.SET, source)
                        value: list[AST.Expression] = [parse_expression(tokens)]
                        while tokens.match(TT.COMMA):
                            value.append(parse_expression(tokens))
                        statements.append(AST.SetStatement((start.span[0], tokens.prev().span[1]), var, value))
                    else:
                        raise NoGrammarMatchError((start.span[0], tokens.prev().span[1]), source, "statement")
        return AST.Block((start_pos, tokens.prev().span[1]), statements, None)

    try:
        file: AST.File = parse_block(TT.EOF, tokens)
    except Error as error: return error
    
    return file

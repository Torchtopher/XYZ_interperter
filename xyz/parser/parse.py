from io import TextIOWrapper
from typing import Iterator
from xyz.parser.error import WrongTokenError
from xyz.tokenizer import Token, TokenType as TT
import xyz.parser.ast as AST
from xyz.error import Error
from xyz.parser.TokenIterator import TokenIterator

# For simplicity, the parser uses the python Exception system instead of an error-as-value system.
# These are converted back to errors-as-values at the top of the parser call stack.

BINARY_TOKENS_TO_AST = {TT.OP_MINUS: AST.BinExpType.SUB, TT.OP_PLUS: AST.BinExpType.ADD}

UNARY_TOKENS_TO_AST = {TT.OP_SIZE: AST.UnExpType.SIZE, TT.OP_NOT: AST.UnExpType.NOT, TT.OP_MINUS: AST.UnExpType.NEG}

def parse(source: TextIOWrapper, tokens: TokenIterator) -> AST.File | Error:

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
    # * / // %
    # unary: ! not # -
    # **

    def parse_expression(tokens: TokenIterator) -> AST.Expression:
        exp = parse_term(tokens)
        return exp

    def parse_term(tokens: TokenIterator) -> AST.Expression: 
        exp = parse_mul_div(tokens)

        while (tokens.match([TT.OP_MINUS, TT.OP_PLUS])):
            t = tokens.prev()
            
            rhs: AST.Expression = parse_mul_div(tokens)
            exp = AST.BinaryExpression(BINARY_TOKENS_TO_AST[t.type], exp, rhs)

        return exp

    def parse_mul_div(tokens: TokenIterator):
        exp = parse_unary(tokens)

        # should we allow multiple unary operators in a row?
        if (tokens.match(TT.OP_MINUS)):
            rhs: AST.Expression = parse_expression(tokens)
            return AST.UnaryExpression(AST.UnExpType.NEG, rhs)

        if (tokens.match(TT.OP_NOT)):
            rhs: AST.Expression = parse_expression(tokens)
            return AST.UnaryExpression(AST.UnExpType.NOT, rhs)

        if (tokens.match(TT.OP_SIZE)):
            rhs: AST.Expression = parse_expression(tokens)
            return AST.UnaryExpression(AST.UnExpType.SIZE, rhs)
        
        return exp

    def parse_unary(tokens: TokenIterator):

        # should we allow multiple unary operators in a row?
        while (tokens.match([TT.OP_MINUS,
                             TT.OP_NOT,
                             TT.OP_SIZE])):
            t = tokens.prev()
            rhs: AST.Expression = parse_unary(tokens)
            return AST.UnaryExpression(UNARY_TOKENS_TO_AST[t.type], rhs)
        
        exp = parse_primary(tokens)

        return exp

    def parse_primary(tokens: TokenIterator) -> AST.Expression: 
        if (tokens.match(TT.INT)):
            t = tokens.prev()
            return AST.LitInt(t.name)
      
        if (tokens.match(TT.FLOAT)):
            t = tokens.prev()
            return AST.LitFloat(t.name)
        
        if (tokens.match(TT.IDENT)):
            t = tokens.prev()
            return AST.VarExpr(t.name)  
        
        if (tokens.match(TT.PAREN_OPEN)):
            exp = parse_expression(tokens)
            tokens.expect(TT.PAREN_CLOSE, source)
            return AST.GroupedExpr(exp)

        # expected more than just ident but close enough
        raise WrongTokenError(tokens.curr().span, source, TT.IDENT)
             

    print(tokens)

    try:
        file: AST.File = parse_expression(tokens)
        tokens.expect(TT.EOF, source)
    except Error as error: return error
    
    return file

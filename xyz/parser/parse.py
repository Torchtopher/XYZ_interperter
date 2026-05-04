from io import TextIOWrapper
from typing import Iterator
from xyz.tokenizer import Token, TokenType
import xyz.parser.ast as AST
from xyz.error import Error
from xyz.parser.error import WrongTokenError
from xyz.parser.TokenIterator import TokenIterator

# For simplicity, the parser uses the python Exception system instead of an error-as-value system.
# These are converted back to errors-as-values at the top of the parser call stack.

def parse(source: TextIOWrapper, tokens: TokenIterator) -> AST.File | Error:

    # ---

    def parse_expression(tokens: TokenIterator) -> AST.Expression:
        
        return None

    def parse_term() -> AST.Expression: 
        pass

    def parse_factor() -> AST.Expression: 
        pass

    print(tokens)

    try:
        file: AST.File = parse_expression(tokens)
        tokens.expect(TokenType.EOF)
    except Error as error: return error
    
    return file

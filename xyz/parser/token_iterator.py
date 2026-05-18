"""
A utility for iterating over tokens.
"""

from xyz.tokenizer import Token, TokenType
from xyz.parser.error import WrongTokenError
from io import StringIO


class TokenIterator:
    """A wrapper around a `list[Token]` to support parsing. Keeps track of an index and provides
    convience functions.

    Raises:
        WrongTokenError: When the token type does not match
    """
    
    data: list[Token]

    def __init__(self, data: list[Token]):
        self.data = data
        self.index = 0

    
    def __isEnd(self):
        return len(self.data) == self.index + 1

    
    def peek(self) -> Token:
        """Returns the next token if exists, otherwise current, does not move index

        Returns:
            Token: The next token to process
        """
        
        if self.__isEnd():
            return self.data[self.index] 
        else:
            return self.data[self.index+1]
    
    def curr(self) -> Token:
        """The token the . Does not move index.

        Returns:
            Token: Token at current index
        """
        
        return self.data[self.index]

    
    def prev(self, n = 1) -> Token:
        """Retruns the Nth previous token. Does not move index.

        Args:
            n (int, optional): How many tokens back to return. Defaults to 1.

        Returns:
            Token: The Nth previous token. 
        """
        assert self.index >= n, "tried to call previous when nothing is before, almost ceratinly a bug?"
        return self.data[self.index-n]

    def back(self) -> Token:
        """ Returns previous token. DOES move index back one.

        Returns:
            Token: The previous token.
        """
        assert self.index != 0, "tried to call back when nothing is before, almost ceratinly a bug?"
        self.index -= 1
        return self.curr()

    def next(self) -> Token:
        """Returns the current token. DOES move index forward one.

        Returns:
            Token: The current token before the index was incremented.
        """
        self.index += 1
        return self.prev()
    
    def check(self, token_type: TokenType) -> bool:
        """Compares the current token type, to `token_type`. Does not move index.

        Args:
            token_type (TokenType): The type to compare to

        Returns:
            bool: If the token type at the current index is the same as `token_type`
        """
        
        return self.data[self.index].type == token_type

    def match(self, token_type: TokenType | list[TokenType]) -> bool:
        """Returns true if current token is the type passed in. DOES move index forward one if so.

        Args:
            token_type (TokenType | list[TokenType]): The type or list of acceptable token types.

        Returns:
            bool: True if the current token type matched `token_type`, else False
        """
        token_types = token_type if isinstance(token_type, list) else [token_type]
        if self.data[self.index].type in token_types:
            self.index += 1
            return True
        
        return False
    
    def expect(self, token_type: TokenType | list[TokenType], source: StringIO) -> Token:
        """Checks that token at the current index is correct. DOES increment index by 1 if so.

        Args:
            token_type (TokenType | list[TokenType]): The type or list of acceptable token types.
            source (StringIO): The source file, needed for errors

        Raises:
            WrongTokenError: When the token type does not match `token_type`

        Returns:
            Token: The token that was succesfully matched against `token_type`
        """
        
        token_types = token_type if isinstance(token_type, list) else [token_type]
        if not self.data[self.index].type in token_types:
            raise WrongTokenError(self.data[self.index].span, source, token_types)
        else:
            if not self.__isEnd(): self.index += 1
            return self.data[min(len(self.data)-1, self.index-1)]

    def __repr__(self):
        return self.data.__repr__()

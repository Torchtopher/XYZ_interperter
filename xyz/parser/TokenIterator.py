
from xyz.tokenizer import Token, TokenType
from xyz.parser.error import WrongTokenError
from io import TextIOWrapper


# want to be able to call next and also previous, 
# so hold data in a list and just keep track of the indexing 
class TokenIterator:

    data: list[Token]

    def __init__(self, data: list[Token]):
        self.data = data
        self.index = 0

    
    def isEnd(self):
        return len(self.data) == self.index + 1

    # gives next if exists, otherwise current, does not move
    def peek(self):
        if self.isEnd():
            return self.data[self.index] 
        else:
            return self.data[self.index+1]
    
    def curr(self):
        return self.data[self.index]

    # gives previous, does not move
    def prev(self):
        assert self.index != 0, "tried to call previous when nothing is before, almost ceratinly a bug?"
        return self.data[self.index-1]

    # gives you current token and moves forward one
    def next(self):
        self.index += 1
        return self.prev()
    
    # checks the current token type, does not move
    def check(self, token_type: TokenType):
        return self.data[self.index].type == token_type

    # True if current token is the type passed in, moves forward one if so
    def match(self, token_type: TokenType | list[TokenType]):
        token_type = [token_type] if type(token_type) != list else token_type
        if self.data[self.index].type in token_type:
            if not self.isEnd(): self.index += 1
            return True
        
        return False
    
    # @TODO, moved here, not sure if it still works as intended 
    # checks that token is correct, moves forward by 1 if so
    def expect(self, token_type: TokenType, source: TextIOWrapper) -> Token | WrongTokenError:
        if not self.data[self.index].type == token_type:
            raise WrongTokenError(self.data[self.index+1], source, self.data[self.index].type)
        else:
            return self.data[self.index]


    def __repr__(self):
        return self.data.__repr__()
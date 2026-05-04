
from xyz.tokenizer import Token, TokenType


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
    
    # gives previous, does not move
    def prev(self):
        assert self.index != 0, "tried to call previous when nothing is before, almost ceratinly a bug?"
        return self.data[self.index-1]

    # gives you current token and moves forward one
    def move(self):
        self.index += 1
        return self.prev()
    
    # True if current token is the type passed in
    def match(self, token_type: TokenType):
        return self.data[self.index].type == token_type
    

    def expect(self, token_type: TokenType) -> Token | WrongTokenError:
        if not self.data[self.index] == token_type:
            raise WrongTokenError(token[1], source, type)
        else:
            return self.data[self.index]


    def __repr__(self):
        return self.data.__repr__()
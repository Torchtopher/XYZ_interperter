from enum import Enum
from io import StringIO
from xyz.error import Error
from xyz.tokenizer import tokenize
from xyz.parser import parse, TokenIterator
from xyz.interpreter import XYZInterpreter, XYZType
from xyz.env import XYZEnvironment

class BuildStep(Enum):
    TOKENIZE = 0
    PARSE = 1
    EXECUTE = 2

def eval(string: str, env: XYZEnvironment | None = None) -> XYZType:
    file = StringIO(string)
    tokens = tokenize(file)
    if isinstance(tokens, Error):
        tokens.print()
        return None
    else:
        tree = parse(file, TokenIterator(tokens))
        if isinstance(tree, Error):
            tree.print()
            return None
        else:
            interp = XYZInterpreter(env)
            return interp.execute_ast(tree)

def debug(string: str, step: BuildStep = BuildStep.EXECUTE, env: XYZEnvironment | None = None):
    file = StringIO(string)
    tokens = tokenize(file)
    if isinstance(tokens, Error):
        tokens.print()
    elif step == BuildStep.TOKENIZE:
        print(tokens)
        return tokens
    else:
        tree = parse(file, TokenIterator(tokens))
        if isinstance(tree, Error):
            tree.print()
        elif step == BuildStep.PARSE:
            print(tree)
            return tree
        else:
            interp = XYZInterpreter(env, True)
            result = interp.execute_ast(tree)
            print(result)
            return result

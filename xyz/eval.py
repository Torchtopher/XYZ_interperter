from enum import Enum
from io import StringIO
from xyz.error import Error
from xyz.tokenizer import tokenize
from xyz.parser import parse, TokenIterator
from xyz.interpreter import XYZInterpreter, XYZType
from xyz.env import XYZEnvironment
from xyz.display import display

class BuildStep(Enum):
    """At which step the build process should stop (and therefore what it should return)."""

    TOKENIZE = 0
    """After tokenizing; returning a stream of tokens"""

    PARSE = 1
    """After parsing; returning an AST"""

    EXECUTE = 2
    """After executing; returning the script's return value"""

def eval(string: str, env: XYZEnvironment | None = None) -> XYZType:
    """Evaluates a given XYZ file.

    Args:
      string:
        The XYZ string to evaluate, interpreted as a file.
      env:
        An optional XYZEnvironment, to provide external values to the global scope.

    Returns:
      The return value of the file.
    """
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
            interp = XYZInterpreter(env, file)
            result = interp.execute_ast(tree)
            if isinstance(result, Error):
                result.print()
                return None
            else:
                return result

def debug(string: str, step: BuildStep = BuildStep.EXECUTE, env: XYZEnvironment | None = None):
    """Prints the result of building a given XYZ file to the provided step, for debugging only.

    Args:
      string:
        The XYZ string to evalaute, interpreted as a file.
      env:
        The optional XYZEnvironment, to provide external values to the global scope.
    """
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
            interp = XYZInterpreter(env, file, True)
            result = interp.execute_ast(tree)
            if isinstance(result, Error):
                result.print()
                return None
            else:
                print(display(result))
                return result

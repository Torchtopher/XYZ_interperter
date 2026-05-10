from abc import abstractmethod
from types import FunctionType
from typing import NamedTuple
from xyz.interpreter.scoped_env import Scope
import xyz.parser.ast as AST

type XYZType = None | bool | int | float | str | FunctionType | dict

# @TODO change asserts to whatever error handling we want

def ensure_num(var: XYZType) -> int | float:
    assert isinstance(var, int | float), f"{var} must be a number, is {type(var)}"
    return var

def ensure_int(var: XYZType) -> int:
    assert isinstance(var, int), f"{var} must be an integer, is {type(var)}"
    return var

def ensure_concat(var: XYZType) -> int | float | str:
    assert isinstance(var, int | float | str), f"{var} must be a number or string, is {type(var)}"
    return var

def ensure_table(var: XYZType) -> dict:
    assert isinstance(var, dict), f"{var} must be a table, is {type(var)}"
    return var

def ensure_func(var: XYZType) -> FunctionType:
    assert isinstance(var, FunctionType), f"{var} must be a function, is {type(var)}"
    return var

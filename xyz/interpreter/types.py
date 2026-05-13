from types import FunctionType
from xyz.interpreter.scoped_env import Scope

type XYZType = None | bool | int | float | str | FunctionType | dict

def printable_type(value: XYZType) -> str:
    if value == None: return "nil"
    if isinstance(value, int) and not isinstance(value, bool): return "int"
    if isinstance(value, float): return "float"
    if value == True or value == False: return "bool"
    if isinstance(value, str): return "string"
    if isinstance(value, FunctionType): return "function"
    if isinstance(value, dict): return "table"

def is_int(var: XYZType) -> bool:
    return isinstance(var, int) and not isinstance(var, bool)
def is_num(var: XYZType) -> bool:
    return is_int(var) or isinstance(var, float)
def can_concat(var: XYZType) -> bool:
    return isinstance(var, int | float | str) and not isinstance(var, bool)

def truthy(var: XYZType) -> bool:
    return var is not None and var is not False

def equals(a: XYZType, b: XYZType) -> bool:
    return type(a) == type(b) and a == b

def ensure_int(var: XYZType) -> int:
    assert isinstance(var, int), f"{var} must be an integer, is {type(var)}"
    return var

def ensure_table(var: XYZType) -> dict:
    assert isinstance(var, dict), f"{var} must be a table, is {type(var)}"
    return var

def ensure_func(var: XYZType) -> FunctionType:
    assert isinstance(var, FunctionType), f"{var} must be a function, is {type(var)}"
    return var

"""
Utilities for type checking in XYZ.
"""

from types import FunctionType
from xyz.interpreter.scoped_env import Scope
from xyz.interpreter.error import LoopRangeError

"""
The underlying Python types for all XYZ values.
"""
type XYZType = None | bool | int | float | str | FunctionType | dict

def printable_type(value: XYZType) -> str:
    """
    Returns a string representation of an XYZ value's type.
    """
    if value == None: return "nil"
    if isinstance(value, int) and not isinstance(value, bool): return "int"
    if isinstance(value, float): return "float"
    if value == True or value == False: return "bool"
    if isinstance(value, str): return "string"
    if isinstance(value, FunctionType): return "function"
    if isinstance(value, dict): return "table"

def is_int(var: XYZType) -> bool:
    """
    Returns whether the XYZ value is an int.
    """
    return isinstance(var, int) and not isinstance(var, bool)

def is_num(var: XYZType) -> bool:
    """
    Returns whether the XYZ value is an int or float.
    """
    return is_int(var) or isinstance(var, float)

def can_concat(var: XYZType) -> bool:
    """
    Returns whether the XYZ value can be concatenated into a string.
    """
    return isinstance(var, int | float | str) and not isinstance(var, bool)

def truthy(var: XYZType) -> bool:
    """
    Returns whether the XYZ value is truthy (not falsey).

    The only falsey values in XYZ are nil and false.
    """
    return var is not None and var is not False

def equals(a: XYZType, b: XYZType) -> bool:
    """
    Returns whether two XYZ values are equal.

    Since in Python booleans are integers, we must also check they have the same type, so 0 != false
    """
    return type(a) == type(b) and a == b

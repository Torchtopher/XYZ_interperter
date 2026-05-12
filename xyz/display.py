from types import FunctionType
from xyz.interpreter.types import XYZType
from re import match

def display(value: XYZType, quote_strings: bool = False) -> str:
    if value == None: return "nil"
    if isinstance(value, int | float) and not isinstance(value, bool): return str(value)
    if value == True: return "true"
    if value == False: return "false"
    if isinstance(value, str): return f'"{value}"' if quote_strings else value
    if isinstance(value, FunctionType): return "<function>"
    if isinstance(value, dict): return display_table(value)

def display_table(table: dict) -> str:
    out = "{ "
    index = 0
    broken_sequence = False
    int_keys: list[int] = []
    other_keys: list[XYZType] = []
    printed: list[str] = []
    for key in table.keys():
        if isinstance(key, int) and not isinstance(key, bool): int_keys.append(key)
        else: other_keys.append(key)
    int_keys.sort()
    for key in int_keys:
        if not broken_sequence and key == index:
            printed.append(display(table[key], True))
            index += 1
        else:
            broken_sequence = True
            printed.append(f"[{display(key, True)}] = {display(table[key], True)}")
    for key in other_keys:
        if isinstance(key, str) and match("[a-zA-Z_][a-zA-Z0-9_]*", key):
            printed.append(f"{key} = {display(table[key], True)}")
        else:
            printed.append(f"[{display(key, True)}] = {display(table[key], True)}")
    out += ", ".join(printed)
    out += " }"
    return out

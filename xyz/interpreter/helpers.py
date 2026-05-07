import numbers

# @TODO change asserts to whatever error handling we want

def ensure_num(var):
    if type(var) != list:
        var = [var]

    for v in var:
        assert isinstance(v, numbers.Number), f"{v} must be a number, is {type(v)}"

def ensure_int(var):
    if type(var) != list:
        var = [var]
    
    for v in var:
        assert isinstance(v, int), "Must be an integer"

def ensure_concat(var):
    if type(var) != list:
        var = [var]

    for v in var:
        assert isinstance(v, str) or isinstance(v, numbers.Number) , f"{v} must be a string or number to concatante"


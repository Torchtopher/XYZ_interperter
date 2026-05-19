"""
Error definitions for the interpreter.
"""

from xyz.error import Error

class OperationTypeError(Error):
    """
    An error returned when an operator receives a value of the wrong type (e.x. trying to add strings)

    Attributes:
      op:
        A string representation of the operation.
      bad_type:
        A string representation of the type that could not be operated on.
    """
    op: str
    bad_type: str

    def __init__(self, span, file, op, bad_type):
        self.op = op
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot apply operator %s to %s" % (self.op, self.bad_type)

class LoopRangeError(Error):
    """
    An error returned when the start, end, or step values for a for loop are not integers.
    """
    def message(self) -> str:
        return "Loop range values must be integers"

class CallSourceError(Error):
    """
    An error returned when a non-function value is called.

    Attributes:
      bad_type:
        A string representation of the type that could not be called.
    """
    bad_type: str

    def __init__(self, span, file, bad_type):
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot call %s" % self.bad_type

class IndexSourceError(Error):
    """
    An error returned when a non-table value is indexed.

    Attributes:
      bad_type:
        A string representation of the type that could not be indexed.
    """
    bad_type: str

    def __init__(self, span, file, bad_type):
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot index %s" % self.bad_type

class UnboundVariableError(Error):
    """
    An error returned when attempting to assign to a nonexistent variable.

    Attributes:
      name:
        The name of the unbound variable.
    """
    name: str

    def __init__(self, span, file, name):
        self.name = name
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot access unbound variable %s" % self.name

class VariableRedefinitionError(Error):
    """
    An error returned when attempting to define a variable that already exists in the same scope.

    Attributes:
      name:
        The name of the variable.
    """
    name: str

    def __init__(self, span, file, name):
        self.name = name
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Variable %s already exists" % self.name

class ConstAssignError(Error):
    """
    An error returned when attempting to assign to a constant variable.

    Attributes:
      name:
        The name of the constant variable.
    """
    name: str

    def __init__(self, span, file, name):
        self.name = name
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot assign to constant variable %s" % self.name

class MismatchedAssignError(Error):
    """
    An error returned when attempting to assign a list of values to a list of variables of different length.

    For example, a list of 3 values cannot be assigned to 2 variables:
    x, y = 1, 2, 3 -- error
    """
    def message(self) -> str:
        return "Mismatched variable and value lists"

class BreakOutsideLoopError(Error):
    """
    An error returned when using the break keyword outside a loop.

    For example,
    let a = 1
    break
    let b = 2 
    """
    def message(self) -> str:
        return "Can not call break outside a loop"

class UncaughtPythonError(Error):
    """An error returned when an unhandled Python exception is raised. 

    Useful to not show the entire call stack, and provide context for the error and its location. 
    For example there is no specific divide by 0 error in XYZ. Until that is implemented, 
    this will be raised with the message "ZeroDivisionError('division by zero')", as well as the line number.
    """

    def __init__(self, span, file, orignal):
        self.orig_error = orignal
        Error.__init__(self, span, file)
    
    def message(self) -> str:
        return f"Type: {type(self.orig_error).__name__} \nInfo: {str(self.orig_error)}"
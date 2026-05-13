from xyz.error import Error

class OperationTypeError(Error):
    op: str
    bad_type: str

    def __init__(self, span, file, op, bad_type):
        self.op = op
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot apply operator %s to %s" % (self.op, self.bad_type)

class LoopRangeError(Error):
    def message(self) -> str:
        return "Loop range values must be integers"

class CallSourceError(Error):
    bad_type: str

    def __init__(self, span, file, bad_type):
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot call %s" % self.bad_type

class IndexSourceError(Error):
    bad_type: str

    def __init__(self, span, file, bad_type):
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot index %s" % self.bad_type

class UnboundVariableError(Error):
    name: str

    def __init__(self, span, file, name):
        self.name = name
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot access unbound variable %s" % self.name

class VariableRedefinitionError(Error):
    name: str

    def __init__(self, span, file, name):
        self.name = name
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Variable %s already exists" % self.name

class ConstAssignError(Error):
    name: str

    def __init__(self, span, file, name):
        self.name = name
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot assign to constant variable %s" % self.name

class MismatchedAssignError(Error):
    def message(self) -> str:
        return "Mismatched variable and value lists"

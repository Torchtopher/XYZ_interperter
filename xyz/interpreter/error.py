from xyz.error import Error

class BinaryOperationTypeError(Error):
    op: str
    bad_type: str

    def __init__(self, span, file, op, bad_type):
        self.op = op
        self.bad_type = bad_type
        Error.__init__(self, span, file)

    def message(self) -> str:
        return "Cannot apply operator %s to %s" % (self.op, self.bad_type)

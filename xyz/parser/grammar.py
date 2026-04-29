type Expression = None

class File:
    expr: Expression

    def __init__(self, expr):
        self.expr = expr

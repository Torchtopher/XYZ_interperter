from xyz.interpreter.error import UnboundVariableError, VariableRedefinitionError, ConstAssignError

class Variable:

    def __init__(self, value, const=False):
        self.const: bool = const
        self.value = value


class Scope:

    def __init__(self, parent, name: str):
        if parent: assert isinstance(parent, Scope), f"Can not assign type {type(parent)} to be the parent of a Scope"
        self.parent: Scope | None = parent
        self.table: dict[str, Variable] = {}
        self.name = name

    def __repr__(self):
        return f"Scope {self.name} with table {self.table} and parent {self.parent}"

    def resolve_var(self, name):
        if name in self.table:
            return self.table[name]

        if self.parent is not None:
            return self.parent.resolve_var(name)

        return None

    def get(self, name, span, source):
        res = self.resolve_var(name)
        if res is None:
            raise UnboundVariableError(span, source, name)
        return res.value

    def define(self, name: str, val, span, source, const=False):
        if name in self.table:
            raise VariableRedefinitionError(span, source, name)

        self.table[name] = Variable(val, const)

    # intended for supplying an environment, should not be run by XYZ code
    def external_define(self, name: str, val):
        self.table[name] = Variable(val, True)

    def update(self, name: str, val, span, source):
        res = self.resolve_var(name)
        if res is None:
            raise UnboundVariableError(span, source, name)
        if res.const:
            raise ConstAssignError(span, source, name)
        res.value = val

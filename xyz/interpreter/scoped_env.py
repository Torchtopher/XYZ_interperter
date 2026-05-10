
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
    
    def get(self, name):
        res = self.resolve_var(name)
        if res is None:
            raise RuntimeError(f"Trying to access unbound variable: {name}")
        return res.value

    def define(self, name: str, val, const=False):
        if name in self.table:
            raise RuntimeError(f"Can not redefine variable with name: {name}")

        self.table[name] = Variable(val, const)

    def update(self, name: str, val):
        res = self.resolve_var(name)
        if res is None:
            raise RuntimeError(f"Trying to set unbound variable: {name}")
        
        if res.const:
            raise RuntimeError(f"Trying to update const variable {name}")
        res.value = val
        

            
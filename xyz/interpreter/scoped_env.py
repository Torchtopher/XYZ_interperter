"""
A scope where XYZ variables are stored.
"""

from xyz.interpreter.error import UnboundVariableError, VariableRedefinitionError, ConstAssignError

class Variable:

    def __init__(self, value, const=False):
        self.const: bool = const
        self.value = value


class Scope:
    """A wrapper around a dictionary. Uses the parent Scope for variables not found in this one.
    """

    def __init__(self, parent, name: str):
        if parent: assert isinstance(parent, Scope), f"Can not assign type {type(parent)} to be the parent of a Scope"
        self.parent: Scope | None = parent
        self.table: dict[str, Variable] = {}
        self.name = name

    def __repr__(self):
        return f"Scope {self.name} with table {self.table} and parent {self.parent}"

    def resolve_var(self, name: str) -> Variable | None:
        """Finds the Variable object for `name`, checking parent scopes until found or global scope hit.

        Args:
            name (str): The name of the variable, used to look it up in `self.__table`

        Returns:
            Variable | None: The Variable object assoicated with `name`, OR None.
        """
        
        if name in self.table:
            return self.table[name]

        if self.parent is not None:
            return self.parent.resolve_var(name)

        return None

    def get(self, name, span, source):
        """Gets the value of variable

        Args:
            name (_type_): _description_
            span (_type_): _description_
            source (_type_): _description_

        Raises:
            UnboundVariableError: When the variable name can not be found in `resolve_var`

        Returns:
            _type_: _description_
        """
        
        res = self.resolve_var(name)
        if res is None:
            raise UnboundVariableError(span, source, name)
        return res.value

    def define(self, name: str, val, span, source, const=False):
        """D

        Args:
            name (str): _description_
            val (_type_): _description_
            span (_type_): _description_
            source (_type_): _description_
            const (bool, optional): If the value should be const. Defaults to False.

        Raises:
            VariableRedefinitionError: When the variable has already been defined
        """
        
        if name in self.table:
            raise VariableRedefinitionError(span, source, name)

        self.table[name] = Variable(val, const)

    def update(self, name: str, val, span, source):
        """_summary_

        Args:
            name (str): _description_
            val (_type_): _description_
            span (_type_): _description_
            source (_type_): _description_

        Raises:
            UnboundVariableError: _description_
            ConstAssignError: _description_
        """
        
        res = self.resolve_var(name)
        if res is None:
            raise UnboundVariableError(span, source, name)
        if res.const:
            raise ConstAssignError(span, source, name)
        res.value = val

    # intended for external interaction (i.e. supplying an environment), should not be run by XYZ code
    def external_define(self, name: str, val, const=True):
        """
        Defines a variable with a value without checking if it exists (so it can't throw an error).
        Should only be run by external code, for example to add an external global variable.
        """
        self.table[name] = Variable(val, const)

    def external_get(self, name: str):
        """
        Gets the value of a variable, throwing a Python RuntimeError if it doesn't exist instead of an XYZ error.
        Should only be run by external code.
        """
        res = self.resolve_var(name)
        if res is None:
            raise RuntimeError("Cannot access unbound variable %s" % name)
        else:
            return res.value

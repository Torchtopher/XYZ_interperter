"""
The main logic of the interpreter.
"""

from types import FunctionType
import xyz.parser.ast as AST
import numbers
from xyz.error import Error, Span
from xyz.interpreter.types import XYZType, Scope, is_num, is_int, truthy, equals, can_concat, printable_type
from xyz.interpreter.error import OperationTypeError, LoopRangeError, CallSourceError, IndexSourceError, MismatchedAssignError
from xyz.display import display
from typing import NamedTuple, TypeAlias, assert_type
from io import StringIO

from xyz.interpreter.scoped_env import Scope
from itertools import zip_longest

class AccessorResult(NamedTuple):
    table: Scope | dict
    key: XYZType

class BreakSignal(Exception):
    pass
class ReturnValue(Exception):
    value: XYZType
    def __init__(self, value: XYZType):
        self.value = value


class XYZInterpreter:
    """
    An instance of the XYZ interpreter.

    Attributes:
      debug:
        Whether the interpreter is in debug mode, in which case it will print some undefined debug text.
      source_file:
        The source file as StringIO for error reporting.
    """

    debug: bool
    source_file: StringIO

    def __init__(self, GVT: Scope|None = None, source_file: StringIO = StringIO(""), debug: bool = False):
        """Creates an instance of the XYZInterpreter

        Args:
            GVT (Scope | None, optional): A `Scope` object that the global variable table will be set to on initalization. Defaults to None.
            source_file (StringIO, optional): The content of the file being run, needed for detailed error messages. Defaults to StringIO("").
            debug (bool, optional): Flag to enable debug printouts. Defaults to False.
        """
        
        # global variable table
        self.GVT: Scope = Scope(None, "global") if not GVT else GVT
        self.source_file = source_file

        # current variable table
        self.CVT: Scope = self.GVT

        self.debug = debug

    # mimics lua in the following ways
    # if len(args) < len(paramaters), fills the rest of the params with None
    # if len(args) > len(parameters), remaining args are ignored, unless there is ...something
    def __xyz_function(self, params: list[str], extra: str | None, block: AST.Block, scope: Scope, name: str, span: Span):
        def call(*args: list[XYZType]) -> XYZType:
            old_cvt = self.CVT

            try:
                self.CVT = Scope(scope, name)
                for var, val in zip_longest(params, args):
                    if var is None:
                        break
                    self.CVT.define(var, val, span, self.source_file)

                # want to bind all the rest of the variables to whatever extra is
                if extra:
                    val_list = args[len(params):]
                    val_dict = {}
                    for i in range(len(val_list)):
                        val_dict[i] = val_list[i]

                    self.CVT.define(extra, val_dict, span, self.source_file)

                self.__execute_block(block)
                return None
            except ReturnValue as r:
                return r.value
            finally:
                self.CVT = old_cvt
        return call

    def eval_expression(self, expr: AST.Expression) -> XYZType:
        """Evaulates an expression and returns the value

        Args:
            expr (AST.Expression): The expression to evaluate

        Raises:
            CallSourceError: When attempting to call a function on a non function type (i.e. int)
            OperationTypeError: When using a binary or unary operator on an unsupported type
            IndexSourceError: When trying to access a non table object (i.e. a=1 a.b) 
            
        Returns:
            XYZType: The value of the expression 
        """
        
        if isinstance(expr, AST.LitFalse):
            return False
        elif isinstance(expr, AST.LitTrue):
            return True
        elif isinstance(expr, AST.LitNil):
            return None
        elif isinstance(expr, AST.LitInt | AST.LitFloat | AST.LitString):
            return expr.value
        elif isinstance(expr, AST.LitTable):
            table: dict[XYZType, XYZType] = {}
            for key, val in expr.value:
                key = self.eval_expression(key)
                val = self.eval_expression(val)
                table[key] = val
            return table

        elif isinstance(expr, AST.FunctionCall):
            args = []

            # whether the function is called with `:` instead of `.` to pass the containing table as the first argument
            if expr.method:
                assert isinstance(expr.source, AST.Access), "Expected function called with ':' (a:b()) to have an access"
                accessor_res: AccessorResult = self.__find_accessor(expr.source)
                assert isinstance(accessor_res.table, dict)
                args.append(accessor_res.table) # table that holds the function we are about to call
                func: FunctionType = accessor_res.table[accessor_res.key] # type: ignore
            else:
                source: XYZType = self.eval_expression(expr.source)
                if isinstance(source, FunctionType):
                    func: FunctionType = source
                else:
                    raise CallSourceError(expr.span, self.source_file, printable_type(source))

            for arg in expr.args:
                args.append(self.eval_expression(arg))

            return func(*args)

        elif isinstance(expr, AST.Lambda):
            return self.__xyz_function(expr.parameters, expr.extra, expr.block, self.CVT, "lambda", expr.span)


        elif isinstance(expr, AST.UnaryExpression):
            val = self.eval_expression(expr.right)
            match expr.type:
                case AST.UnExpType.NOT:
                    return not truthy(val)

                case AST.UnExpType.NEG:
                    if isinstance(val, int | float) and not isinstance(val, bool):
                        return -val
                    else:
                        raise OperationTypeError(expr.span, self.source_file, "-", printable_type(val))

                case AST.UnExpType.SIZE:
                    if isinstance(val, dict):
                        return len(val)
                    else:
                        raise OperationTypeError(expr.span, self.source_file, "#", printable_type(val))

        elif isinstance(expr, AST.BinaryExpression):

            match expr.type:
                # ===== can only be performed with numbers (floats and ints) ========
                case AST.BinExpType.ADD: # +
                    return self.__arith_helper(expr, lambda a, b: a + b, is_num, "+")
                case AST.BinExpType.SUB: # -
                    return self.__arith_helper(expr, lambda a, b: a - b, is_num, "-")
                case AST.BinExpType.MUL: # *
                    return self.__arith_helper(expr, lambda a, b: a * b, is_num, "*")
                case AST.BinExpType.DIV: # /
                    return self.__arith_helper(expr, lambda a, b: a / b, is_num, "/")
                case AST.BinExpType.FLOORDIV: # //
                    return self.__arith_helper(expr, lambda a, b: a // b, is_num, "//")
                case AST.BinExpType.EXP: # **
                    return self.__arith_helper(expr, lambda a, b: a ** b, is_num, "**")
                case AST.BinExpType.MOD: # %
                    return self.__arith_helper(expr, lambda a, b: a % b, is_num, "%")

                case AST.BinExpType.LESS:
                    return self.__arith_helper(expr, lambda a, b: a < b, is_num, "<")
                case AST.BinExpType.LEQ:
                    return self.__arith_helper(expr, lambda a, b: a <= b, is_num, "<=")
                case AST.BinExpType.GREATER:
                    return self.__arith_helper(expr, lambda a, b: a > b, is_num, ">")
                case AST.BinExpType.GEQ:
                    return self.__arith_helper(expr, lambda a, b: a >= b, is_num, ">=")

                # ===== can only be perfomed with 2 ints ========
                case AST.BinExpType.BIT_AND:
                    return self.__arith_helper(expr, lambda a, b: a & b, is_int, "&")
                case AST.BinExpType.BIT_XOR:
                    return self.__arith_helper(expr, lambda a, b: a ^ b, is_int, "^")
                case AST.BinExpType.BIT_OR:
                    return self.__arith_helper(expr, lambda a, b: a | b, is_int, "|")
                case AST.BinExpType.LSHIFT:
                    return self.__arith_helper(expr, lambda a, b: a << b, is_int, "<<")
                case AST.BinExpType.RSHIFT:
                    return self.__arith_helper(expr, lambda a, b: a >> b, is_int, ">>")

                # all objects
                case AST.BinExpType.EQUAL:
                    return equals(self.eval_expression(expr.left), self.eval_expression(expr.right))
                case AST.BinExpType.NEQ:
                    return not equals(self.eval_expression(expr.left), self.eval_expression(expr.right))
                case AST.BinExpType.AND:
                    v1 = self.eval_expression(expr.left)
                    if not truthy(v1):
                        return v1
                    else:
                        return self.eval_expression(expr.right)
                case AST.BinExpType.OR:
                    v1 = self.eval_expression(expr.left)
                    if truthy(v1):
                        return v1
                    else:
                        return self.eval_expression(expr.right)

                # works with strings and numbers only
                case AST.BinExpType.CONCAT:
                    return self.__arith_helper(expr, lambda a, b: display(a) + display(b), can_concat, "..")

        elif isinstance(expr,  AST.Var):
            return self.CVT.get(expr.name, expr.span, self.source_file)

        elif isinstance(expr, AST.Access):
            if expr.index == None: return self.eval_expression(expr.source)
            index = self.eval_expression(expr.index)
            container = self.__ensure_index_source(expr)
            return container[index] if index in container else None

    def __arith_helper(self, exp: AST.BinaryExpression, op_function: FunctionType, check: FunctionType, op_str: str) -> XYZType:
        v1 = self.eval_expression(exp.left)
        v2 = self.eval_expression(exp.right)
        if check(v1) and check(v2):
            return op_function(v1, v2)
        else:
            raise OperationTypeError(exp.span, self.source_file, op_str, printable_type(v1) if not check(v1) else printable_type(v2))

    def exec_statement(self, stmnt: AST.Statement):
        """Runs a statement using the current `Scope` set in this object  

        Args:
            stmnt (AST.Statement): AST of Statement to run 

        Raises:
            MismatchedAssignError: When the variables and values of an assignment are not equal in length (i.e a, b = 1)
            LoopRangeError: If the start, stop or step of a loop is not an integer
            BreakSignal: To signal the break out of a loop 
        """
        
        if isinstance(stmnt, AST.Definition):
            if len(stmnt.var) != len(stmnt.value): raise MismatchedAssignError(stmnt.span, self.source_file)
            for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                val = self.eval_expression(expr)
                self.CVT.define(var.name, val, stmnt.span, self.source_file, stmnt.const)

        elif isinstance(stmnt, AST.SetStatement):
            if len(stmnt.var) != len(stmnt.value): raise MismatchedAssignError(stmnt.span, self.source_file)
            var: AST.Access
            expr: AST.Expression
            for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                access: AccessorResult = self.__find_accessor(var)
                val = self.eval_expression(expr)
                # this means that we are doing assignment to something like
                # a = 1
                if isinstance(access.table, Scope):
                    # need to repect const
                    assert isinstance(access.key, str)
                    access.table.update(access.key, val, stmnt.span, self.source_file)

                # this case is for something like
                # a.b = 2, since eval(a) is a dict with like {"b": 42}
                else:
                    assert type(access.table) == dict, f"how is this: {type(access.table)}"
                    access.table[access.key] = val

        elif isinstance(stmnt, AST.ForLoop):
            start = self.__check_loop_range(stmnt.start)
            end = self.__check_loop_range(stmnt.end)
            step = self.__check_loop_range(stmnt.step)

            for i in range(start, end, step):
                old_cvt = self.CVT
                self.CVT = Scope(self.CVT, "for loop")
                self.CVT.define(stmnt.var, i, stmnt.span, self.source_file)
                try:
                    self.__execute_block(stmnt.block)
                except BreakSignal:
                    break
                finally:
                    self.CVT = old_cvt

        elif isinstance(stmnt, AST.FunctionCall):
            # want to just call the function for side effects
            self.eval_expression(stmnt)

        elif isinstance(stmnt, AST.Break):
            raise BreakSignal

        elif isinstance(stmnt, AST.Block):
            old_cvt = self.CVT

            self.CVT = Scope(self.CVT, "inner block")
            try:
                self.__execute_block(stmnt)
            finally:
                self.CVT = old_cvt

        elif isinstance(stmnt, AST.WhileLoop):
            while (truthy(self.eval_expression(stmnt.condition))):
                old_cvt = self.CVT
                self.CVT = Scope(self.CVT, "While loop")
                try:
                    self.__execute_block(stmnt.block)
                except BreakSignal:
                    break
                finally:
                    self.CVT = old_cvt

        elif isinstance(stmnt, AST.RepeatLoop):
            while True:
                old_cvt = self.CVT
                self.CVT = Scope(self.CVT, "Repeat loop")
                try:
                    self.__execute_block(stmnt.block)
                except BreakSignal:
                    break
                finally:
                    self.CVT = old_cvt

                if truthy(self.eval_expression(stmnt.condition)): break

        elif isinstance(stmnt, AST.IfStatement):
            old_cvt = self.CVT

            self.CVT = Scope(self.CVT, "If statement")
            try:
                stop = False

                for expr, block in stmnt.conditions:
                    if truthy(self.eval_expression(expr)):
                        self.__execute_block(block)
                        stop = True
                        break
                if not stop and stmnt.else_block:
                    self.__execute_block(stmnt.else_block)

            finally:
                self.CVT = old_cvt

    def __check_loop_range(self, expr: AST.Expression) -> int:
        value = self.eval_expression(expr)
        if not isinstance(value, int) or isinstance(value, bool):
            raise LoopRangeError(expr.span, self.source_file)
        else:
            return value

    def __ensure_index_source(self, expr: AST.Access) -> dict:
        val = self.eval_expression(expr.source)
        if not isinstance(val, dict):
            raise IndexSourceError(expr.span, self.source_file, printable_type(val))
        else:
            return val

    # basically the same as evaulating an expression, but this time give back the container and key
    # so the caller can set the value themselves
    def __find_accessor(self, access_expr: AST.Access) -> AccessorResult:
        if access_expr.index is None:
            assert isinstance(access_expr.source, AST.Var), "with no index, the expression to be set must be a variable"
            return AccessorResult(self.CVT, access_expr.source.name)

        key = self.eval_expression(access_expr.index)

        return AccessorResult(self.__ensure_index_source(access_expr), key)


    def __execute_block(self, ast: AST.Block):
        for statement in ast.statements:
            self.exec_statement(statement)
            if self.debug: print(self.GVT)
        if ast.return_statement != None:
            raise ReturnValue(self.eval_expression(ast.return_statement))

    def execute_ast(self, ast: AST.File) -> XYZType | Error:
        """The entrypoint for running an XYZ program, given the AST

        Args:
            ast (AST.File): The parsed AST to run

        Returns:
            XYZType | Error: The return value of the program OR the error that occured
        """
        try:
            self.__execute_block(ast)
        except ReturnValue as r:
            return r.value
        except Error as e:
            return e

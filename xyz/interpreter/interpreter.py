from types import FunctionType
import xyz.parser.ast as AST
import numbers
from xyz.interpreter.types import XYZType, Scope, ensure_concat, ensure_int, ensure_num, ensure_table, ensure_func
from typing import NamedTuple, TypeAlias, assert_type

from xyz.interpreter.scoped_env import Scope
from itertools import zip_longest

TEST_AST: AST.File = AST.Block(
      statements=[
          AST.Definition(
              const=False,
              var=[AST.Var("a")],
              value=[AST.LitInt(1)],
          ),
          AST.SetStatement(
              var=[AST.Access(AST.Var("a"), None)],
              value=[AST.LitInt(2)],
          ),
      ],
      return_statement=AST.Var("a"),
  )

# TEST_AST: AST.File = AST.Block(
#       statements=[],
#       return_statement=AST.Access(
#           AST.Access(
#               AST.Var("a"),
#               AST.Access(
#                   AST.Var("fx_result"),
#                   AST.LitString("c"),
#               ),
#           ),
#           AST.LitString("b"),
#       ),
#   )

# a[f(x).c].b
# access(acesss("a", acesss(f(x), "c")) , "b")

# ee(expr.right) lookup is
# GVT["a"]["f(x)"]["c"]["b"]

# most inner "source", that is not an access is the first lookup
# then it goes first lookup index top to bottom (i.e if access chain keep looking up as you go down (f(x) then C in this case))
# then go up go up one, take the result of the most inner one and apply the index chain lookup on it

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

    debug: bool

    def __init__(self, GVT: Scope|None = None, debug: bool = False):
        # global variable table
        self.GVT: Scope = Scope(None, "global") if not GVT else GVT

        # current variable table
        self.CVT: Scope = self.GVT

        self.debug = debug

    # mimics lua in the following ways
    # if len(args) < len(paramaters), fills the rest of the params with None
    # if len(args) > len(parameters), remaining args are ignored, unless there is ...something
    def xyz_function(self, params: list[str], extra: str | None, block: AST.Block, scope: Scope, name: str):
        def call(*args: list[XYZType]) -> XYZType:
            old_cvt = self.CVT

            try:
                self.CVT = Scope(scope, name)
                for var, val in zip_longest(params, args):
                    if var is None:
                        break
                    self.CVT.define(var, val)

                # want to bind all the rest of the variables to whatever extra is
                if extra:
                    val_list = args[len(params):]
                    val_dict = {}
                    for i in range(len(val_list)):
                        val_dict[i] = val_list[i]

                    self.CVT.define(extra, val_dict)

                self.execute_block(block)
                return None
            except ReturnValue as r:
                return r.value
            finally:
                self.CVT = old_cvt
        return call

    def eval_expression(self, expr: AST.Expression) -> XYZType:
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
                accessor_res: AccessorResult = self.find_accessor(expr.source)
                assert isinstance(accessor_res.table, dict)
                args.append(accessor_res.table) # table that holds the function we are about to call
                func: FunctionType = accessor_res.table[accessor_res.key] # type: ignore # genuinely the best i could do
            else:
                func: FunctionType = ensure_func(self.eval_expression(expr.source))

            assert type(func) == FunctionType, f"Trying to call something that is not a function {expr.source}"
            for arg in expr.args:
                args.append(self.eval_expression(arg))

            return func(*args)

        elif isinstance(expr, AST.Lambda):
            return self.xyz_function(expr.parameters, expr.extra, expr.block, self.CVT, "lambda")


        elif isinstance(expr, AST.UnaryExpression):
            val = self.eval_expression(expr.ee(expr.right))
            match expr.type:
                case AST.UnExpType.NOT:
                    # allowed to take unary not of everything, just want to make sure its not None
                    return val is not None

                case AST.UnExpType.NEG:
                    assert isinstance(val, int | float), f"attempt to perform arithmetic on a {type(val)} value"
                    return -val

                case AST.UnExpType.SIZE:
                    assert isinstance(val, dict), f"attempt to get length of a {type(val)} value"
                    return len(val)

        elif isinstance(expr, AST.BinaryExpression):

            ee = self.eval_expression
            
            match expr.type:
                # ===== can only be performed with numbers (floats and ints) ========
                case AST.BinExpType.ADD: # +
                    return ensure_num(ee(expr.left)) + ensure_num(ee(expr.right))
                case AST.BinExpType.SUB: # -
                    return ensure_num(ee(expr.left)) - ensure_num(ee(expr.right))
                case AST.BinExpType.MUL: # *
                    return ensure_num(ee(expr.left)) * ensure_num(ee(expr.right))
                case AST.BinExpType.DIV: # /
                    return ensure_num(ee(expr.left)) / ensure_num(ee(expr.right))
                case AST.BinExpType.FLOORDIV: # //
                    return int(ensure_num(ee(expr.left)) // ensure_num(ee(expr.right)))
                case AST.BinExpType.EXP: # **
                    return ensure_num(ee(expr.left)) ** ensure_num(ee(expr.right))
                case AST.BinExpType.MOD: # %
                    return ensure_num(ee(expr.left)) % ensure_num(ee(expr.right))

                case AST.BinExpType.LESS:
                    return ensure_num(ee(expr.left)) < ensure_num(ee(expr.right))
                case AST.BinExpType.LEQ:
                    return ensure_num(ee(expr.left)) <= ensure_num(ee(expr.right))
                case AST.BinExpType.GREATER:
                    return ensure_num(ee(expr.left)) > ensure_num(ee(expr.right))
                case AST.BinExpType.GEQ:
                    return ensure_num(ee(expr.left)) >= ensure_num(ee(expr.right))

                # ===== can only be perfomed with 2 ints ========
                case AST.BinExpType.BIT_AND:
                    return ensure_int(ee(expr.left)) & ensure_int(ee(expr.right))
                case AST.BinExpType.BIT_XOR:
                    return ensure_int(ee(expr.left)) ^ ensure_int(ee(expr.right))
                case AST.BinExpType.BIT_OR:
                    return ensure_int(ee(expr.left)) | ensure_int(ee(expr.right))
                case AST.BinExpType.LSHIFT:
                    return ensure_int(ee(expr.left)) << ensure_int(ee(expr.right))
                case AST.BinExpType.RSHIFT:
                    return ensure_int(ee(expr.left)) >> ensure_int(ee(expr.right))

                # all objects
                case AST.BinExpType.EQUAL:
                    return ee(expr.left) == ee(expr.right)
                case AST.BinExpType.NEQ:
                    return ee(expr.left) != ee(expr.right)
                case AST.BinExpType.AND:
                    return ee(expr.left) and ee(expr.right)
                case AST.BinExpType.OR:
                    return ee(expr.left) or ee(expr.right)

                # works with strings and numbers only
                case AST.BinExpType.CONCAT:
                    return str(ensure_concat(ee(expr.left))) + str(ensure_concat(ee(expr.right)))

        elif isinstance(expr,  AST.Var):
            return self.CVT.get(expr.name)

        elif isinstance(expr, AST.Access):
            container = self.eval_expression(expr.source)
            if expr.index == None: return container
            index = self.eval_expression(expr.index)
            return ensure_table(container)[index] if index in ensure_table(container) else None


    # @TODO add line and character numebrs to the AST so we can give better error messages
    def exec_statement(self, stmnt: AST.Statement):
        if isinstance(stmnt, AST.Definition):
            if len(stmnt.var) != len(stmnt.value): raise RuntimeError("Must have same number of variables and expressions to assign")
            for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                val = self.eval_expression(expr)
                self.CVT.define(var.name, val, stmnt.const)

        elif isinstance(stmnt, AST.SetStatement):
            if len(stmnt.var) != len(stmnt.value): raise RuntimeError("Must have same number of variables and expressions to assign")
            var: AST.Access
            expr: AST.Expression
            for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                access: AccessorResult = self.find_accessor(var)
                val = self.eval_expression(expr)
                # this means that we are doing assignment to something like
                # a = 1
                if isinstance(access.table, Scope):
                    # need to repect const
                    assert isinstance(access.key, str)
                    access.table.update(access.key, val)

                # this case is for something like
                # a.b = 2, since eval(a) is a dict with like {"b": 42}
                else:
                    assert type(access.table) == dict, f"how is this: {type(access.table)}"
                    access.table[access.key] = val

        elif isinstance(stmnt, AST.ForLoop):
            start = self.eval_expression(stmnt.start)
            end = self.eval_expression(stmnt.end)
            step = self.eval_expression(stmnt.step)

            old_cvt = self.CVT

            self.CVT = Scope(self.CVT, "for loop")
            self.CVT.define(stmnt.var, start)

            try:
                for i in range(ensure_int(start), ensure_int(end), ensure_int(step)):
                    self.CVT.update(stmnt.var, i)
                    try:
                        self.execute_ast(stmnt.block)
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
                self.execute_block(stmnt)
            finally:
                self.CVT = old_cvt

        elif isinstance(stmnt, AST.WhileLoop):
            old_cvt = self.CVT

            self.CVT = Scope(self.CVT, "While loop")
            try:
                while (self.eval_expression(stmnt.condition)):
                    try:
                        self.execute_block(stmnt.block)
                    except BreakSignal:
                        break
            finally:
                self.CVT = old_cvt

        elif isinstance(stmnt, AST.RepeatLoop):
            old_cvt = self.CVT

            self.CVT = Scope(self.CVT, "Repeat loop")
            try:
                while True:
                    try:
                        self.execute_block(stmnt.block)
                    except BreakSignal:
                        break

                    if self.eval_expression(stmnt.condition): break
            finally:
                self.CVT = old_cvt

        elif isinstance(stmnt, AST.IfStatement):
            old_cvt = self.CVT

            self.CVT = Scope(self.CVT, "If statement")
            try:
                stop = False

                for expr, block in stmnt.conditions:
                    if (self.eval_expression(expr)):
                        self.execute_block(block)
                        stop = True
                        break
                if not stop and stmnt.else_block:
                    self.execute_block(stmnt.else_block)

            finally:
                self.CVT = old_cvt

    # basically the same as evaulating an expression, but this time give back the container and key
    # so the caller can set the value themseleves
    def find_accessor(self, access_expr: AST.Access) -> AccessorResult:
        if access_expr.index is None:
            assert isinstance(access_expr.source, AST.Var), "with no index, the expression to be set must be a variable"
            return AccessorResult(self.CVT, access_expr.source.name)

        container = self.eval_expression(access_expr.source)
        key = self.eval_expression(access_expr.index)

        return AccessorResult(ensure_table(container), key)


    def execute_block(self, ast: AST.Block):
        for statement in ast.statements:
            self.exec_statement(statement)
            if self.debug: print(self.GVT)
        if ast.return_statement != None:
            raise ReturnValue(self.eval_expression(ast.return_statement))

    def execute_ast(self, ast: AST.File) -> XYZType:
        try:
            self.execute_block(ast)
        except ReturnValue as r:
            return r.value

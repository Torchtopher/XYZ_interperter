import xyz.parser.ast as AST
import numbers
from xyz.interpreter.helpers import ensure_concat, ensure_int, ensure_num
from typing import NamedTuple

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

# right lookup is
# GVT["a"]["f(x)"]["c"]["b"]

# most inner "source", that is not an access is the first lookup
# then it goes first lookup index top to bottom (i.e if access chain keep looking up as you go down (f(x) then C in this case))
# then go up go up one, take the result of the most inner one and apply the index chain lookup on it

class AccessorResult(NamedTuple):
    table: Scope | dict
    key: any

class FunctionInfo():

    def __init__(self, params, extra, block, scope, name="Unnamed Function"):
        self.parameters: list[str] = params
        self.extra: str | None = extra
        self.block: AST.Block = block
        self.scope: Scope = scope
        self.name: str = name

class BreakSignal(Exception):
    pass

class XYZInterperter:

    def __init__(self, GVT:Scope=None):
        # global variable table
        self.GVT: Scope = Scope(None, "global") if not GVT else GVT
        
        # current variable table
        self.CVT: Scope = self.GVT 

    # mimics lua in the following ways
    # if len(args) < len(paramaters), fills the rest of the params with None
    # if len(args) > len(parameters), remaining args are ignored, unless there is ...something
    def _call_func(self, func_info: FunctionInfo, args: list):
        old_cvt = self.CVT

        try:
            self.CVT = Scope(func_info.scope, func_info.name)
            for var, val in zip_longest(func_info.parameters, args):
                if var is None:
                    break
                self.CVT.define(var, val)
            
            # want to bind all the rest of the variables to whatever extra is
            if func_info.extra:
                val_list = args[len(func_info.parameters):]
                val_dict = {}
                for i in range(len(val_list)):
                    val_dict[i] = val_list[i]

                self.CVT.define(func_info.extra, val_dict)

            return self.execute_ast(func_info.block)

        finally:
            self.CVT = old_cvt

    def eval_expression(self, expr: AST.Expression):
        match type(expr):
            case AST.LitFalse:
                return False
            case AST.LitTrue:
                return True
            case AST.LitNil:
                return None
            case AST.LitInt | AST.LitFloat | AST.LitString:
                return expr.value
            case AST.LitTable:
                table = {}
                for key, val in expr.value:
                    key = self.eval_expression(key)
                    val = self.eval_expression(val)
                    table[key] = val
                return table

            case AST.FunctionCall:
                args = []

                # whether the function is called with `:` instead of `.` to pass the containing table as the first argument
                if expr.method:
                    assert type(expr.source) == AST.Access, "Expected function called with ':' (a:b()) to have an access" 
                    accessor_res: AccessorResult = self.find_accessor(expr.source) 
                    args = [accessor_res.table] # table that holds the function we are about to call
                    func_info: FunctionInfo = accessor_res.table[accessor_res.key]
                else:
                    func_info: FunctionInfo = self.eval_expression(expr.source)
                
                assert type(func_info) == FunctionInfo, f"Trying to call something that is not a function {expr.source}"
                for arg in expr.args:
                    args.append(self.eval_expression(arg))

                return self._call_func(func_info, args)

            case AST.Lambda:
                return FunctionInfo(expr.parameters, expr.extra, expr.block, self.CVT)
                

            case AST.UnaryExpression:
                val = self.eval_expression(expr.right)
                match expr.type:
                    case AST.UnExpType.NOT:
                        assert val is True or val is False or val is None, f"Can not take unary not of type {type(val)}"
                        return not val
                        
                    case AST.UnExpType.NEG:
                        assert isinstance(val, numbers.Number), f"attempt to perform arithmetic on a {type(val)} value"
                        return -val
                    
                    case AST.UnExpType.SIZE:
                        assert type(val) == dict, f"attempt to get length of a {type(val)} value"
                        return len(val)

            case AST.BinaryExpression:
                left = self.eval_expression(expr.left)
                right = self.eval_expression(expr.right)
                match expr.type:
                    # ===== can only be performed with numbers (floats and ints) ========
                    case AST.BinExpType.ADD: # + 
                        ensure_num([left, right])
                        return left + right
                    case AST.BinExpType.SUB: # -
                        ensure_num([left, right])
                        return left - right
                    case AST.BinExpType.MUL: # *
                        ensure_num([left, right])
                        return left * right
                    case AST.BinExpType.DIV: # /
                        ensure_num([left, right])
                        return left / right
                    case AST.BinExpType.FLOORDIV: # //
                        ensure_num([left, right])
                        return left // right
                    case AST.BinExpType.EXP: # **
                        ensure_num([left, right])
                        return left ** right
                    case AST.BinExpType.MOD: # %
                        ensure_num([left, right])
                        return left % right
                    
                    case AST.BinExpType.LESS: 
                        ensure_num([left, right])
                        return left < right
                    case AST.BinExpType.LEQ:
                        ensure_num([left, right])
                        return left <= right
                    case AST.BinExpType.GREATER:
                        ensure_num([left, right])
                        return left > right
                    case AST.BinExpType.GEQ:
                        ensure_num([left, right])
                        return left >= right

                    # ===== can only be perfomed with 2 ints ========
                    case AST.BinExpType.BIT_AND:
                        ensure_int([left, right])
                        return left & right
                    case AST.BinExpType.BIT_XOR:
                        ensure_int([left, right])
                        return left ^ right
                    case AST.BinExpType.BIT_OR:
                        ensure_int([left, right])
                        return left | right
                    case AST.BinExpType.LSHIFT:
                        ensure_int([left, right])
                        return left << right
                    case AST.BinExpType.RSHIFT:
                        ensure_int([left, right])
                        return left >> right

                    # all objects
                    case AST.BinExpType.EQUAL:
                        return left == right
                    case AST.BinExpType.NEQ:
                        return left != right
                    case AST.BinExpType.AND:
                        return left and right
                    case AST.BinExpType.OR:
                        return left or right
                    
                    # works with strings and numbers only
                    case AST.BinExpType.CONCAT:
                        ensure_concat([left, right])
                        return str(left) + str(right)
                    case _:
                        print(f"ERROR: Unhandled binary expression with type {expr.type}")
                        exit(-1)

            case AST.Var:
                return self.CVT.get(expr.name)
            
            case AST.Access:
                container = self.eval_expression(expr.source)
                index = self.eval_expression(expr.index)
                return container if index == None else (container[index] if index in container else None)

            case _:
                print(f"UNHANDLED EXPR CASE: {type(expr)}")
                
                    
    # @TODO add line and character numebrs to the AST so we can give better error messages
    def exec_statement(self, stmnt: AST.Statement):
        match type(stmnt):
            case AST.Definition:
                if len(stmnt.var) != len(stmnt.value): raise RuntimeError("Must have same number of variables and expressions to assign")
                for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                    val = self.eval_expression(expr)
                    self.CVT.define(var.name, val, stmnt.const)     

            case AST.SetStatement:
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
                        access.table.update(access.key, val)

                    # this case is for something like
                    # a.b = 2, since eval(a) is a dict with like {"b": 42}
                    else:
                        assert type(access.table) == dict, f"how is this: {type(access.table)}" 
                        access.table[access.key] = val 
            
            case AST.ForLoop:
                start = self.eval_expression(stmnt.start)
                end = self.eval_expression(stmnt.end)
                step = self.eval_expression(stmnt.step)
                assert type(start) == type(end) == type(step) == int, "For loops must have interger parameters!"

                old_cvt = self.CVT

                self.CVT = Scope(self.CVT, "for loop")
                self.CVT.define(stmnt.var, start)

                try: 
                    for i in range(start, end, step):
                        self.CVT.update(stmnt.var, i)
                        try:
                            self.execute_ast(stmnt.block)
                        except BreakSignal:
                            break
                finally:
                    self.CVT = old_cvt
            
            case AST.FunctionCall:
                # want to just call the function for side effects
                self.eval_expression(stmnt)

            case AST.Break:
                raise BreakSignal
            
            case AST.Block:
                old_cvt = self.CVT

                self.CVT = Scope(self.CVT, "inner block")
                try:
                    self.execute_ast(stmnt)
                finally:
                    self.CVT = old_cvt

            case AST.WhileLoop:
                old_cvt = self.CVT

                self.CVT = Scope(self.CVT, "While loop")
                try:
                    while (self.eval_expression(stmnt.condition)):
                        try:
                            self.execute_ast(stmnt.block)
                        except BreakSignal:
                            break
                finally:
                    self.CVT = old_cvt
            
            case AST.RepeatLoop:
                old_cvt = self.CVT

                self.CVT = Scope(self.CVT, "Repeat loop")
                try:
                    while True:
                        try:
                            self.execute_ast(stmnt.block)
                        except BreakSignal:
                            break

                        if self.eval_expression(stmnt.block): break
                finally:
                    self.CVT = old_cvt

            case AST.IfStatement:
                old_cvt = self.CVT

                self.CVT = Scope(self.CVT, "If statement")
                try:
                    stop = False

                    for expr, block in stmnt.conditions:
                        if (self.eval_expression(expr)):
                            self.execute_ast(block)
                            stop = True
                            break
                    if not stop and stmnt.else_block:
                        self.execute_ast(stmnt.else_block)
                    
                finally:
                    self.CVT = old_cvt

    # basically the same as evaulating an expression, but this time give back the container and key
    # so the caller can set the value themseleves 
    def find_accessor(self, access_expr: AST.Access) -> AccessorResult:
        if access_expr.index is None:
            assert type(access_expr.source) == AST.Var, "with no index, the expression to be set must be a variable"
            return AccessorResult(self.CVT, access_expr.source.name)
        
        container = self.eval_expression(access_expr.source)
        key = self.eval_expression(access_expr.index)

        return AccessorResult(container, key)
            
            
    def execute_ast(self, ast: AST.File):
        for statement in ast.statements:
            self.exec_statement(statement)
            print(self.GVT)
        
        return self.eval_expression(ast.return_statement)

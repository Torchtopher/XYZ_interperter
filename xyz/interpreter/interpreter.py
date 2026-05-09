import xyz.parser.ast as AST
import numbers
from xyz.interpreter.helpers import ensure_concat, ensure_int, ensure_num
from typing import NamedTuple

TEST_AST: AST.File = AST.Block(
    [
        AST.SetStatement([AST.Access(AST.Var("a"), None)], [AST.LitInt(10)]),
        AST.SetStatement([AST.Access(AST.Var("b"), None )], [AST.LitInt(11)]),
    ],
    AST.Var("b")
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
    table: dict
    key: any
    
class XYZInterperter:

    def __init__(self, GVT:dict=None):
        # global variable table
        self.GVT = {} if not GVT else GVT

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
                print("ERROR NOT IMPLEMENTED YET")
            case AST.Lambda:
                print("ERROR NOT IMPLEMENTED YET")

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
                return self.GVT[expr.name]
            
            case AST.Access:
                container = self.eval_expression(expr.source)
                index = self.eval_expression(expr.index)
                return container[index]

            case _:
                print(f"UNHANDLED EXPR CASE: {type(expr)}")
                
                    
    # @TODO add line and character numebrs to the AST so we can give better error messages
    def exec_statement(self, stmnt: AST.Statement):
        match type(stmnt):
            case AST.SetStatement:
                if len(stmnt.var) != len(stmnt.value): raise RuntimeError("Must have same number of variables and expressions to assign")
                var: AST.VarExpr
                expr: AST.Expression
                for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                    access: AccessorResult = self.find_accessor(var)
                    val = self.eval_expression(expr)
                    access.table[access.key] = val   


    # basically the same as evaulating an expression, but this time give back the container and key
    # so the caller can set the value themseleves 
    def find_accessor(self, access_expr: AST.Access) -> AccessorResult:
        if access_expr.index is None:
            assert type(access_expr.source) == AST.Var, "with no index, the expression to be set must be a variable"
            return AccessorResult(self.GVT, access_expr.source.name)
        
        container = self.eval_expression(access_expr.source)
        key = self.eval_expression(access_expr.index)
        print(container)
        print(key)
        return AccessorResult(container, key)
            
            
    def execute_ast(self, ast: AST.File):
        ast = TEST_AST 
        
        print("Using TEST_AST INSTEAD of passed in AST")
            
        for statement in ast.statements:
            self.exec_statement(statement)
            print(self.GVT)
        
        return self.eval_expression(ast.return_statement)

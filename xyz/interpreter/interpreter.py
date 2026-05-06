import xyz.parser.ast as AST

TEST_AST: AST.File = AST.Block(
    [
        AST.SetStatement([AST.Access(AST.Var("a"), None)], [AST.LitInt(10)]),
        AST.SetStatement([AST.Access(AST.Var("b"), None)], [AST.LitInt(11)]),
    ],
    AST.Var("b")
)


def execute_ast(ast: AST.File):
    ast = TEST_AST 
    
    print("Using TEST_AST INSTEAD of passed in AST")
    
    global_var_table = {}
    

    def evaluate_expression(expr: AST.Expression):
        match type(expr):
            case AST.LitFalse:
                return False
            case AST.LitTrue:
                return True
            case AST.LitNil:
                return None
            case AST.LitInt | AST.LitFloat | AST.LitString:
                return expr.value
            
            case _:
                print(f"UNHANDLED EXPR CASE: {type(expr)}")
            
    # gets the value of a variable, including accessors
    def getVarExpr(var: AST.VarExpr):
        
        
    # sets the value of a variable
    def setVarExpr(var: AST.VarExpr, value):
        if var.accessors: # something like a.b.c, b and c will be in accessors
            # accessing the most inner dict to update 
            dict_to_update = global_var_table[var.name] 
            for accessor in var.accessors[:-1]:
                dict_to_update = dict_to_update[accessor]
            dict_to_update[var.accessors[-1]] = value
                
        global_var_table[var.name] = value
                    
    
    # @TODO add line and character numebrs to the AST so we can give better error messages
    def execute_statement(stmnt: AST.Statement):
        match type(stmnt):
            case AST.SetStatement:
                if len(stmnt.var) != len(stmnt.value): raise RuntimeError("Must have same number of variables and expressions to assign")
                var: AST.VarExpr
                expr: AST.Expression
                for var, expr in zip(stmnt.var, stmnt.value, strict=True):
                    val = evaluate_expression(expr)

    
    for statement in ast.statements:
        execute_statement(statement)
        print(global_var_table)
    
    return evaluate_expression(ast.return_statement)

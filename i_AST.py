class AST(object):
    pass

class Function(AST):
    def __init__(self, name, block, ):
        self.name = name
        self.block = block


class Block(AST):
    def __init__(self,compound_statements):
        self.compound_statements = compound_statements

class Compound(AST):
    def __init__(self):
        self.children = []

class Assign(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Var(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class NoOp(AST):
    pass

class UnaryOp(AST):
    def __init__(self, op, expr):
        self.token = self.op = op
        self.expr = expr

class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class CondOp(AST):
    def __init__(self, cond, thendo, elsedo):
        self.cond = cond
        self.thendo = thendo
        self.elsedo = elsedo

class LoopOp(AST):
    def __init__(self, cond, thendo):
        self.cond = cond
        self.thendo = thendo

class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Array(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class String(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

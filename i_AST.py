# defining the various nodes of the Abstract Syntax Tree
# these are visited by i_interpreter.py

#the base class
class AST(object):
    pass

#a function has a name and a block of code
class Function(AST):
    def __init__(self, ln, name, block):
        self.name = name
        self.block = block
        self.ln = ln;

# a block has a set of compound statements
# this is a little redundant for now
# but i might add in local variable scope stuff here later? idk
class Block(AST):
    def __init__(self, ln, compound_statements):
        self.compound_statements = compound_statements
        self.ln = ln;

# a  has a series of children, which are executed in order
class Compound(AST):
    def __init__(self, ln):
        self.children = []
        self.ln = ln;

# an assignment node has a left child (the variable being assigned)
# and a right child (the value being assigned to the variable)
# as well as an operator (used to distinguish regular assign from array assign)
class Assign(AST):
    def __init__(self, ln, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        self.ln = ln;

# a variable node holds a variable name
class Var(AST):
    def __init__(self, ln, token):
        self.token = token
        self.value = token.value
        self.ln = ln;

# a NoOp doesn't do anything lol
class NoOp(AST):
    pass

# an Unary Operator has an operator and a child expression it operates on
class UnaryOp(AST):
    def __init__(self, ln, op, expr):
        self.token = self.op = op
        self.expr = expr
        self.ln = ln;

# a Binary Operator has an operator and two children that are operated on
class BinOp(AST):
    def __init__(self, ln, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right
        self.ln = ln;

# a Conditional Operator has three children - a condtion, a child that
# is evaluated if the condition is true (i.e. nonzero) and a child that
# is evaluated if the condition is false (i.e. zero)
class CondOp(AST):
    def __init__(self, ln, cond, thendo, elsedo):
        self.cond = cond
        self.thendo = thendo
        self.elsedo = elsedo
        self.ln = ln;

# a Loop Operator as a condition and a child that is operated while the conditoin
# does not evaluate to false (i.e. zero)
class LoopOp(AST):
    def __init__(self, ln, cond, thendo):
        self.cond = cond
        self.thendo = thendo
        self.ln = ln;

# a Num node just holds a float
class Num(AST):
    def __init__(self, ln, token):
        self.token = token
        self.value = token.value
        self.ln = ln;

# an Array node holds an array
class Array(AST):
    def __init__(self, ln, token):
        self.token = token
        self.value = token.value
        self.ln = ln;

# and a String node holds a string
class String(AST):
    def __init__(self, ln, token):
        self.token = token
        self.value = token.value
        self.ln = ln;

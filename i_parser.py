# the parser reads in tokens from the lexer and generates an AST

from i_lexer import *
from i_nodevisitor import *
from i_AST import *

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        # propagate the verbose flag
        self.verbose = lexer.verbose

    # again, note to self, do error handling at some point in the future
    def error(self, errortext):
        raise Exception("Invalid syntax: " + errortext)

    # "eat" a token (verify it matches the expected token, and move on to the next)
    def eat(self, token_type):
        if self.current_token.type == token_type:
            if(self.verbose): print "ate " + str(self.current_token)
            self.current_token = self.lexer.get_next_token()
        else:
            self.error("expecting " + token_type + " got " + str(self.current_token))

    # create a dictionary of all of the functions in a program
    def parsefunctions(self):
        funs = {};
        while self.current_token.type == FUNCTION:
            f =  self.getfunction()
            funs[f.name] = f
        return funs;

    # parse in an entire function (definition and code block)
    def getfunction(self):
        self.eat(FUNCTION)
        #first, get the name
        var_node = self.getvariable()
        fun_name = var_node.value
        #then, get the code
        block_node = self.getblock()
        #create and return the node
        function_node = Function(fun_name, block_node)
        return function_node

    # not too useful right now, basically just parses a compound statement
    # might add something about local variable scope here later
    def getblock(self):
        compound_statement_node = self.getcompound_statement()
        node = Block(compound_statement_node)
        return node

    # parse in all of the statements in a block
    def getcompound_statement(self):
        if self.verbose: print "starting compound statement: " + str(self.current_token)
        self.eat(LBRACKET)
        if (self.verbose): print "beginning compound statement"
        # get a list of statements
        nodes = self.getstatement_list()
        self.eat(RBRACKET)
        root = Compound()
        for node in nodes:
            root.children.append(node)
        return root

    # go through, statement by statement, adding them to an array of nodes
    def getstatement_list(self):
        #get the first statement
        node = self.getstatement()
        results = [node]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            # if there are more statements, keep going
            if self.current_token.type != RBRACKET:
                results.append(self.getstatement())
        return results

    # parse a full staement
    def getstatement(self):
        if self.verbose: print "getting statement"
        if self.verbose: print "next token: " + str(self.current_token)
        # if it starts another code block, process that
        if self.current_token.type == LBRACKET:
            node = self.getcompound_statement()
        # if it's a variable first, process that
        elif self.current_token.type == ID:
            node = self.procvar()
        # otherwise, process an expression
        else:
            node = self.getexpr()
        return node

    # woah we found a variable
    def procvar(self):
        if self.verbose: print "encountering variable"
        # get the name of it
        varname = self.getexpr();
        # if we're assigning to it, process an assignment statement
        if (self.current_token.type == ASSIGN):
            node = self.getassignment_statement(varname)
        # handle some weird cases
        elif (self.current_token.type == SEMI):
            node = varname
            node.token.type = ARRASSIGN
        # if we're assigning to an index in an array
        else:
            if self.verbose: print "omg what " + self.current_token.value
            node = varname
            node.token.type = ARRASSIGN
            node.left.right = self.current_token
        return node

    # let's deal with condsitional statements
    def parsecond(self):
        conditional = self.getexpr();
        # start with an empty thendo and elsedo
        thendoblock = NoOp()
        elsedoblock = NoOp()
        # read in those blocks if they exist
        if self.current_token.type == THENDO:
            self.eat(THENDO)
            thendoblock = self.getblock();
            if self.current_token.type == ELSEDO:
                self.eat(ELSEDO)
                elsedoblock = self.getblock()
        # create a conditional op node
        node = CondOp(conditional,thendoblock,elsedoblock)
        return node;

    # time to parse while loops
    def parsewhile(self):
        #similar to parsing conditional statements
        conditional = self.getexpr();
        thendoblock = NoOp()
        if self.current_token.type == THENDO:
            self.eat(THENDO)
            thendoblock = self.getblock();
        node = LoopOp(conditional,thendoblock)
        return node;


    # assignment satements
    def getassignment_statement(self, varname):
        if self.verbose: print "getting assignemnt: " + str(self.current_token)
        # left is the variable, right is the expression you are assigning to it
        left = varname
        token = self.current_token
        self.eat(ASSIGN)
        right = self.getexpr()
        # for array assignment
        if not isinstance(left, Var):
            if self.verbose: print "OMFG assigning a array part"
            token = Token(ARRASSIGN, ARRASSIGN)
        node = Assign(left, token, right)
        return node

    # processing a name that is not a string
    def getvariable(self):
        varname = self.current_token
        node = Var(varname)
        self.eat(ID)
        if self.verbose: print "ate an ID"
        # if the next character is a bracket, do that
        if self.current_token.type == ARRAY:
            if self.verbose: print "parsing an array index"
            arr = self.current_token.value
            self.eat(ARRAY)
            aindex = arr[0]
            node = BinOp(left = node, op=Token(INDEX,INDEX), right = aindex)
            # at some point i messed up the code for array assignment? idk
            # it works tho just trust me
            if (self.current_token.type == ASSIGN):
                if self.verbose: print "launching into assignment mode"
                node = self.getassignment_statement(node)
        return node

    # if nothing
    def getempty(self):
        return NoOp()

    # a factor is a small unit of code
    # could be a reserved command, could be a variable, could be a number, etc.
    # the token type tells us what we are dealing with
    def getfactor(self):
        token = self.current_token
        # iterate through and see what token came next
        # first, some unary operators
        if token.type == PLUS:
            self.eat(PLUS)
            node = UnaryOp(token, self.getfactor())
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = UnaryOp(token,self.getfactor())
            return node
        elif token.type == PROMPT:
            self.eat(PROMPT)
            node = UnaryOp(token,self.getexpr())
            return node
        elif token.type == FILEIN:
            self.eat(FILEIN)
            node = UnaryOp(token,self.getexpr())
            return node
        elif token.type == PRINT:
            self.eat(PRINT)
            node = UnaryOp(token,self.getexpr())
            return node
        elif token.type == RANDOM:
            self.eat(RANDOM)
            node = UnaryOp(token,self.getterm())
            return node
        #now, some more complex functions
        elif token.type == CALL:
            self.eat(CALL)
            if self.verbose:print "parsing a call";
            left = self.getfactor()
            right=self.getexpr()
            if isinstance(right, String): right.value = "'" + right.value + "'"
            if self.verbose:print "attempting to pass " + str(right.value) + " to " + str(left.value);
            node = BinOp(left=left,op=token,right=right)
            return node;
        elif token.type == FILEOUT:
            self.eat(FILEOUT)
            left = self.getfactor()
            right = self.getexpr()
            if isinstance(right, String): right.value = "'" + right.value + "'"
            node = BinOp(left=left,op=token,right=right)
            return node;
        elif token.type == RETURN:
            self.eat(RETURN)
            if self.verbose:print "parsing a return";
            right = self.getexpr()
            if isinstance(right, String): right.value = "'" + right.value + "'"
            if self.verbose:print "attempting to return " + str(right)
            if isinstance(right, BinOp):
                right.value = [right.left.value, right.right.value]
            node = UnaryOp(token, right.value)
            return node
        elif token.type==COND:
            self.eat(COND)
            node = self.parsecond()
            return node
        elif token.type==WHILE:
            self.eat(WHILE)
            node = self.parsewhile()
            return node
        elif token.type == FLOAT:
            self.eat(FLOAT)
            return Num(token)
        elif token.type == ARRAY:
            self.eat(ARRAY)
            return Array(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.getexpr()
            self.eat(RPAREN)
            return node
        elif token.type == SEMI:
            #self.eat(SEMI)
            node = Num(Token(FLOAT,0.0))
            return node
        elif token.type == RBRACKET:
            node = Num(Token(FLOAT,0.0))
            return node
        elif token.type == STRING:
            self.eat(STRING)
            if self.verbose: print token
            return String(token)
        # if all else fails, it's probably a variable?
        else:
            node = self.getvariable()
            return node

    # a term is slightly bigger than a factor
    # terms could be like 5*3 or something
    # useful for order of operations
    def getterm(self):
        node = self.getfactor()
        while self.current_token.type in (MUL, DIV, EXPONENT):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            elif token.type == DIV:
                self.eat(DIV)
            elif token.type == EXPONENT:
                self.eat(EXPONENT)
            node = BinOp(left = node, op = token, right = self.getfactor())
        return node

    # get an expression
    # an expression could be 5+3 or 2*5+3
    def getexpr(self):

        node = self.getterm()

        while self.current_token.type in (PLUS, MINUS, CONCAT):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == CONCAT:
                self.eat(CONCAT)
            elif token.type == MINUS:
                self.eat(MINUS)
            node = BinOp(left=node, op = token, right=self.getterm())
        # this is also where we handle comparisons
        if self.current_token.type == EQUALS:
            if self.verbose: print self.current_token
            token = self.current_token
            self.eat(EQUALS)
            node = BinOp(left=node, op=token, right=self.getterm())
        if self.current_token.type == LESSER:
            if self.verbose: print self.current_token
            token = self.current_token
            self.eat(LESSER)
            node = BinOp(left=node, op=token, right=self.getterm())
        if self.current_token.type == GREATER:
            if self.verbose: print self.current_token
            token = self.current_token
            self.eat(GREATER)
            node = BinOp(left=node, op=token, right=self.getterm())
        if self.current_token.type == LESSEREQ:
            if self.verbose: print self.current_token
            token = self.current_token
            self.eat(LESSEREQ)
            node = BinOp(left=node, op=token, right=self.getterm())
        if self.current_token.type == GREATEREQ:
            if self.verbose: print self.current_token
            token = self.current_token
            self.eat(GREATEREQ)
            node = BinOp(left=node, op=token, right=self.getterm())
        return node

    # and here's where the magic happens
    def parse(self):
        # parse in the list of functions
        functions = self.parsefunctions()
        # make sure we reach the end of the file
        if self.current_token.type != EOF and self.current_token.type != SEMI:
            self.error("EOF expected: " + str(self.current_token))
        # return the functions to the interpreter
        return functions

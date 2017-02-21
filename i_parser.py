from i_lexer import *
from i_nodevisitor import *
from i_AST import *

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()
        self.verbose = lexer.verbose

    def error(self, errortext):
        raise Exception("Invalid syntax: " + errortext)


    def eat(self, token_type):
        if self.current_token.type == token_type:
            if(self.verbose): print "ate " + str(self.current_token)
            self.current_token = self.lexer.get_next_token()
        else:
            self.error("expecting " + token_type + " got " + str(self.current_token))

    def parsefunctions(self):
        funs = {};

        while self.current_token.type == FUNCTION:
            f =  self.getfunction()
            funs[f.name] = f
        return funs;



    def getargs(self):
        self.eat(LPAREN)
        args = []
        while self.current_token.type != RPAREN:
            args.append(self.getvariable())
        self.eat(RPAREN)
        return args

    def getfunction(self):
        self.eat(FUNCTION)
        var_node = self.getvariable()
        fun_name = var_node.value
        block_node = self.getblock()
        function_node = Function(fun_name, block_node)
        return function_node




    def getblock(self):
        compound_statement_node = self.getcompound_statement()
        node = Block(compound_statement_node)
        return node

    def getcompound_statement(self):
        if self.verbose: print "starting compound statement: " + str(self.current_token)
        if (self.current_token.type == LBRACKET):
            self.eat(LBRACKET)
            if (self.verbose): print "beginning compound statement"
            nodes = self.getstatement_list()
            self.eat(RBRACKET)
        else:
            nodes = [self.getstatement()]

        root = Compound()
        for node in nodes:
            root.children.append(node)

        return root

    def getstatement_list(self):
        node = self.getstatement()
        results = [node]
        while self.current_token.type == SEMI:
            self.eat(SEMI)
            if self.current_token.type != RBRACKET:
                results.append(self.getstatement())
        return results

    def getstatement(self):
        if self.verbose: print "getting statement"
        if self.verbose: print "next token: " + str(self.current_token)
        if self.current_token.type == LBRACKET:
            node = self.getcompound_statement()
        elif self.current_token.type == ID:

            node = self.procvar()
        else:
            node = self.getexpr()
        return node

    def procvar(self):
        if self.verbose: print "encountering variable"
        varname = self.getexpr();
        if (self.current_token.type == ASSIGN):
            node = self.getassignment_statement(varname)
        elif (self.current_token.type == SEMI):
            #if self.verbose: print "noop: " + str(varname.left.left)
            node = varname
            node.token.type = ARRASSIGN
        else:
            if self.verbose: print "omg what " + self.current_token.value
            node = varname
            node.token.type = ARRASSIGN
            node.left.right = self.current_token

        return node

    def parsecond(self):
        conditional = self.getexpr();
        thendoblock = NoOp()
        elsedoblock = NoOp()
        if self.current_token.type == THENDO:
            self.eat(THENDO)
            thendoblock = self.getblock();
            if self.current_token.type == ELSEDO:
                self.eat(ELSEDO)
                elsedoblock = self.getblock()
        node = CondOp(conditional,thendoblock,elsedoblock)
        return node;

    def parsewhile(self):
        conditional = self.getexpr();
        thendoblock = NoOp()
        if self.current_token.type == THENDO:
            self.eat(THENDO)
            thendoblock = self.getblock();
        node = LoopOp(conditional,thendoblock)
        return node;



    def getassignment_statement(self, varname):
        if self.verbose: print "getting assignemnt: " + str(self.current_token)
        left = varname
        token = self.current_token
        self.eat(ASSIGN)
        right = self.getexpr()

        if not isinstance(left, Var):
            if self.verbose: print "OMFG assigning a array part"
            token = Token(ARRASSIGN, ARRASSIGN)
        node = Assign(left, token, right)

        #if self.verbose: print "parse assign: " + left
        return node

    def getvariable(self):
        varname = self.current_token
        node = Var(varname)
        self.eat(ID)
        if self.current_token.type == ARRAY:
            if self.verbose: print "parsing an array index"
            arr = self.current_token.value
            self.eat(ARRAY)
            aindex = arr[0]
            node = BinOp(left = node, op=Token(INDEX,INDEX), right = aindex)
            if (self.current_token.type == ASSIGN):
                if self.verbose: print "launching into assignment mode"
                node = self.getassignment_statement(node)
        return node

    def getempty(self):
        return NoOp()

    def getfactor(self):
        token = self.current_token
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
        else:
            node = self.getvariable()
            return node

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

    def parse(self):
        functions = self.parsefunctions()
        if self.current_token.type != EOF and self.current_token.type != SEMI:
            print "hm"
            self.error("EOF expected: " + str(self.current_token))
        return functions

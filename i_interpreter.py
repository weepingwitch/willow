from i_parser import *
from i_format_mapper import *
import numbers, re, random
from string import Template

def isnumber(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError) as e:
        return False

def islist(s):
    try:
        list(s)
        return True
    except (ValueError, TypeError) as e:
        return False


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.verbose = parser.verbose
        self.vars = {}
        self.funcs = {}
        self.funcargs = {}



    def visit_Function(self, node):
        if self.verbose: print "attempting function " + str(node)
        self.vars["sysargs"] = self.funcargs[node]
        returnvar = self.visit(node.block)
        if self.verbose: print "Recieved: " + str(returnvar)
        return returnvar

    def visit_Block(self, node):
        return self.visit(node.compound_statements)

    def visit_Compound(self, node):
        if self.verbose: print "visiting compound node " + str(node)
        ret = 0
        for child in node.children:
            ret = (self.visit(child))
        return ret

    def visit_NoOp(self, node):
        pass

    def visit_Assign(self, node):
        if node.token.type == ARRASSIGN:
            if self.verbose: print node.left.left.value
            val = self.visit(node.right)
            myarr = self.vars[node.left.left.value]
            arrindex = node.left.right
            if self.verbose: print "arrayloc: " + str(arrindex)
            if isnumber(arrindex):
                myarr[int(arrindex)] = val
            else:
                arrindex = self.vars[arrindex]
                myarr[int(arrindex)] = val
        else:
            var_name = node.left.value
            val = self.visit(node.right)
            self.vars[var_name] = val
            if (self.verbose):print "assigning " + var_name + "=" + str(val)
        return val

    def visit_Var(self,node):
        var_name = node.value
        val = self.vars.get(var_name)
        if val is None:
            return 0.0;
        else:
            return val

    def visit_UnaryOp(self, node):
        op = node.op.type
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)
        elif op == RETURN:
            argv = node.expr
            if isinstance(argv,str) and argv[0].isalpha and argv[0] not in ('"', "'"):
                argx = self.vars.get(argv)
                argv = argx

            elif isinstance(argv, list):
                argv = self.dofunc(argv[0],argv[1]);
            elif isinstance(argv, str) and argv[0] in ('"', "'"):
                argv = argv[1:-1]
            return argv
        elif op == PRINT:
            print self.visit(node.expr)
            return 0;
        elif op == PROMPT:
            if not isinstance(node.expr, Var):
                prompt = node.expr.value
            else:
                prompt = self.vars[node.expr.value]
            text = raw_input(prompt)
            return text;
        elif op == RANDOM:
            if not isinstance(node.expr, Var):
                maxn = node.expr.value
            else:
                maxn = self.vars[node.expr.value]
            maxn = float(maxn)
            res = random.random() * maxn;
            return res;
        elif op == FILEIN:
            if not isinstance(node.expr, Var):
                fname = node.expr.value
            else:
                fname = self.vars[node.expr.value]
            if self.verbose: print self.fileloc
            if self.verbose: print fname
            f = open(self.fileloc + '/' + fname)
            text = f.read()
            f.close()
            return text;

    def doadd(self, left, right):
        if isnumber(left):
            lval = float(left)
        else:
            lval = left
        if isnumber(right):
             rval = float(right)
        else:
            rval = right
        if (isnumber(lval) and isnumber(rval)) or (isinstance(lval,list) and isinstance(rval, list)):
            return lval + rval
        elif (isnumber(lval) and isinstance(rval, list)):
            res = list(rval)
            if self.verbose: print "adding " + str(lval) + " to " + str(rval)
            for i in rval:
                res[rval.index(i)] = self.doadd( res[rval.index(i)],lval)
            return res
        elif  (isinstance(lval, list) and isnumber(rval)):
            res = list(lval);
            if self.verbose: print "adding " + str(rval) + " to " + str(lval)
            for i in lval:
                #print res[lval.index(i)]
                res[lval.index(i)] = self.doadd( res[lval.index(i)],rval)
            return res
        else:
            return str(lval) + str(rval)

    def dosubtract(self, left, right):
        if isnumber(left):
            lval = float(left)
        else:
            lval = left
        if isnumber(right):
             rval = float(right)
        else:
            rval = right
        if (isnumber(lval) and isnumber(rval)) or (isinstance(lval,list) and isinstance(rval, list)):
            return lval - rval
        elif (isnumber(lval) and isinstance(rval, list)):
            res = list(rval)

            for i in rval:
                res[rval.index(i)] = self.dosubtract( res[rval.index(i)],lval)
            return res
        elif  (isinstance(lval, list) and isnumber(rval)):
            res = list(lval);

            for i in lval:
                #print res[lval.index(i)]
                res[lval.index(i)] = self.dosubtract( res[lval.index(i)],rval)
            return res
        else:
            return str(lval) - str(rval)

    def doconcat(self, left, right):
        lval = self.visit(left)
        rval = self.visit(right)
        if (isnumber(lval) and isnumber(rval)):
            return str(lval) + str(rval)
        elif ((isnumber(lval) or isinstance(lval, str)) and isinstance(rval, list)):
            res = list(rval)
            if self.verbose: print "adding " + str(lval) + " to " + str(rval)
            res.append(lval)
            return res
        elif  (isinstance(lval, list) and (isnumber(rval) or isinstance(rval, str))):
            res = list(lval);
            if self.verbose: print "adding " + str(rval) + " to " + str(lval)
            res.append(rval)
            return res
        elif (isinstance(lval, list) and isinstance(rval, list)):
            return lval + rval
        else:
            return str(lval) + str(rval)


    def domult(self, left, right):
        lval = self.visit(left)
        rval = self.visit(right)
        if isnumber(lval) and isnumber(rval):
            return lval * rval
        elif (isnumber(lval) and isinstance(rval, list)):
            res = list(rval)
            #if self.verbose: print "adding " + str(lval) + " to " + str(rval)
            for i in rval:
                res[rval.index(i)] = res[rval.index(i)] * lval
            return res
        elif  (isinstance(lval, list) and isnumber(rval)):
            res = list(lval);
            #if self.verbose: print "adding " + str(rval) + " to " + str(lval)
            for i in lval:
                #print res[lval.index(i)]
                res[lval.index(i)] = res[lval.index(i)] * rval
            return res
        elif isnumber(lval):
            res =  int(lval) * rval
            return res
        elif isnumber(rval):
            res =  lval * int(rval)
            return res


    def visit_BinOp(self, node):
        res = 0
        if self.verbose: print "trying binaryop node " + str(node.op)
        if node.op.type == PLUS:
            res = self.doadd(self.visit(node.left), self.visit(node.right))
        elif node.op.type == CONCAT:
            res = self.doconcat(node.left, node.right)
        elif node.op.type == CALL:
            if self.verbose: print "interpreting a call " + str(node.left)
            return self.dofunc(node.left.value, node.right.value)
        elif node.op.type == MINUS:
            res = self.dosubtract(self.visit(node.left), self.visit(node.right))
        elif node.op.type == MUL:
            res = self.domult(node.left, node.right)
        elif node.op.type == DIV:
            res =  self.visit(node.left) / self.visit(node.right)
        elif node.op.type == EXPONENT:
            res =  pow(self.visit(node.left),self.visit(node.right))
        elif node.op.type == INDEX:
            if self.verbose: print "trying to interpret an array index " + node.left.value + "[" + str(int(node.right)) + "]"
            arr = self.visit_Var(node.left)
            if isnumber(node.right):
                index = int(node.right)
            elif isinstance(node.right, str):
                index = self.vars[node.right.token]

            if index>=len(arr):
                res = 0
            else:
                res = arr[int(index)]
        elif node.op.type == EQUALS:
            res = (self.visit(node.left) == self.visit(node.right))
            if (res):
                res = 1
            else:
                res = 0
        elif node.op.type == LESSER:
            res = (self.visit(node.left) < self.visit(node.right))
            if (res):
                res = 1
            else:
                res = 0
        elif node.op.type == GREATER:
            res = (self.visit(node.left) > self.visit(node.right))
            if (res):
                res = 1
            else:
                res = 0
        elif node.op.type == LESSEREQ:
            res = (self.visit(node.left) <= self.visit(node.right))
            if (res):
                res = 1
            else:
                res = 0
        elif node.op.type == GREATEREQ:
            res = (self.visit(node.left) >= self.visit(node.right))
            if (res):
                res = 1
            else:
                res = 0
        elif node.op.type == FILEOUT:
            if not isinstance(node.left, Var):
                fname = node.left.value
            else:
                fname = self.vars[node.left.value]
            if self.verbose: print self.fileloc
            if self.verbose: print fname
            f = open(self.fileloc + '/' + fname, "w")
            text = self.visit(node.right)
            f.write(text)
            f.close()
            return text;
        if self.verbose: print "computed binaryop node " + str(node.op)
        if self.verbose: print "result: " + str(res)
        return res

    def visit_CondOp(self, node):
        res = 0;
        if self.verbose: print "trying conditional node "
        if (self.visit(node.cond) != 0):
            res = self.visit(node.thendo)
        else:
            res = self.visit(node.elsedo)
        return res;

    def visit_LoopOp(self, node):
        res = 0;
        if self.verbose: print "trying while loop"
        while(self.visit(node.cond) != 0):
            res = self.visit(node.thendo)
        return res;

    def visit_Num(self, node):
        return node.value


    def visit_String(self, node):
        res = node.value
        if self.verbose: print self.vars
        res = format_map(res, self.vars)

        return res

    def visit_Array(self, node):

        res = list(node.value)

        for s in node.value:
            if isinstance(s,basestring):
                res[node.value.index(s)] = format_map(s, self.vars)
                var = res[node.value.index(s)]
                if islist(var):
                    res[node.value.index(s)] = var

        return res

    def dofunc(self,function,passargs=None):

        function = function.strip('"')
        function = function.strip("'")
        if self.verbose: print "calling a function " +function
        funname = function
        funnode = self.funcs.get(funname)
        #try parsing if a variable is passed
        if funnode == None:
            funnode = self.funcs.get(self.vars[funname])
        if funnode == None:
            return 0.0
        argv = passargs
        if isinstance(argv,str) and argv[0].isalpha and argv[0] not in ('"', "'"):
            argv = self.vars[argv]
        elif isinstance(argv, str) and argv[0] in ('"', "'"):
            argv = argv[1:-1]
        self.funcargs[funnode] = argv
        res = self.visit(funnode)
        if self.verbose: print ("1attempting to return: " + str(res))
        return res

    def interpret(self, args, fileloc):
        self.fileloc = fileloc
        funcs = self.parser.parse()
        self.funcs = funcs
        if self.verbose: print funcs;
        if funcs is None:
            return ''
        if self.verbose: print "storing " + str(args) + " in " + str(funcs['main'])
        self.funcargs[funcs['main']] = args
        self.visit(funcs['main'])

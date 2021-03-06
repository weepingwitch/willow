from i_parser import *
import ast;
from i_format_mapper import *
import numbers, re, random, math, urllib2
from string import Template

# the interpreter navigates the AST by visiting each node and evaluating it
# this then executes the program

# useful to check if a string is a number
def isnumber(s):
    try:
        float(s)
        return True
    except (ValueError, TypeError) as e:
        return False

# useful to check if something is a list
def islist(s):
    try:
        list(s)
        return True
    except (ValueError, TypeError) as e:
        return False

# useful to break a string into bits for string division
def chunkstring(string, length):
    try:
        return (string[0+i:length+i] for i in range(0, len(string), length))
    except (ValueError, TypeError) as e:
        return [0];


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
        self.verbose = parser.verbose
        self.vars = {}
        self.funcs = {}
        self.funcargs = {}


    # visit a function node
    def visit_Function(self, node):
        if self.verbose: print "attempting function " + str(node)
        # store the function args in argv
        #self.vars["argv"] = self.funcargs[node]


        # visit the block of code for the function
        returnvar = self.visit(node.block)
        if self.verbose: print "Recieved: " + str(returnvar)
        return returnvar

    # again, not too useful right now, might add in local scope stuff later
    def visit_Block(self, node):
        return self.visit(node.compound_statements)

    # parse through all of the statements in the block
    def visit_Compound(self, node):
        if self.verbose: print "visiting compound node " + str(node)
        ret = 0
        for child in node.children:
            ret = (self.visit(child))
        return ret

    # do nothing
    def visit_NoOp(self, node):
        return 0

    # visit an assignment node
    def visit_Assign(self, node):
        # if it's assigning to an array
        if node.token.type == ARRASSIGN:
            if self.verbose: print node.left.left.value
            val = self.visit(node.right)
            myarr = self.vars[node.left.left.value]
            arrindex = node.left.right
            if self.verbose: print "arrayloc: " + str(arrindex)
            # see whether the index is a variable or not
            if isnumber(arrindex):
                aindex = int(arrindex)
            else:
                aindex = self.vars[arrindex]
            # if the array is a string, handle that
            if isinstance(myarr, str):
                if self.verbose: print "doing a string"
                myarr = myarr[:aindex] + val + myarr[aindex + 1:]
                self.vars[node.left.left.value] = myarr;
            # otherwise it's a regular array
            else:
                if (int(aindex)>= len(myarr)):
                    while len(myarr) <= int(aindex):
                        myarr.extend([0.0])
                myarr[int(aindex)] = val
        # otherwise, it's a regular assignment statement
        else:
            var_name = node.left.value
            val = self.visit(node.right)
            # store it in the vars dictionary
            self.vars[var_name] = val
            if (self.verbose):print "assigning " + var_name + "=" + str(val)
        return val

    # get a variable from the vars dictionary
    def visit_Var(self,node):
        var_name = node.value
        val = self.vars.get(var_name)
        if val is None:
            # all unitialized variables default to 0
            return 0.0;
        else:
            return val

    # visit an unary operator
    def visit_UnaryOp(self, node):
        op = node.op.type
        # unary plus and minus
        if op == PLUS:
            return +self.visit(node.expr)
        elif op == MINUS:
            return -self.visit(node.expr)
        # return a value
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
        # print statements!
        elif op == PRINT:
            print self.visit(node.expr)
            return node.expr;
        # compute the length of a string or array
        elif op == LEN:
            thing = self.visit(node.expr)
            if (isinstance(thing,list)):
                res = float(len(self.visit(node.expr)))
                return res
            elif (isinstance(thing, str)):
                test = self.vars.get(node.expr.value)
                if test != None:
                    if test[0] == "[":
                        thing = ast.literal_eval(test)
                    else:
                        thing = test;
                res = float(len(thing));
                return res
        # round down a float
        elif op == FLOOR:
            res = float(math.floor(self.visit(node.expr)))
            return res
        # get user input
        elif op == PROMPT:
            #check if the prompt text is a variable
            if not isinstance(node.expr, Var):
                if isinstance(node.expr, BinOp) or isinstance(node.expr, UnaryOp):
                    #handle if it's a compound statement
                    prompt = self.visit(node.expr)
                else:
                    prompt = node.expr.value
            else:
                prompt = self.vars[node.expr.value]
            # prompt the user
            text = raw_input(prompt)
            return text;
        # generate a random float
        elif op == RANDOM:
            # check if the max is a variable
            if not isinstance(node.expr, Var):
                maxn = node.expr.value
            else:
                maxn = self.vars[node.expr.value]
            maxn = float(maxn)
            # generate the number
            res = random.random() * maxn;
            return res;
        # read in a file
        elif op == FILEIN:
            # check if file name is a variable
            if not isinstance(node.expr, Var):
                fname = self.visit(node.expr)
            else:
                fname = self.vars[node.expr.value]
            if self.verbose: print self.fileloc
            if self.verbose: print fname
            #handle a web file
            if "http" in fname:
                response = urllib2.urlopen(fname)
                text = response.read()
            else:
                #open a local file
                try:
                    f = open( fname)
                    text = f.read()
                    f.close()
                except:
                    text = 0.0;
            # return the contents
            return text;

    # handles adding two things
    def doadd(self, left, right):
        # check if the things are numbers
        if isnumber(left):
            lval = float(left)
        else:
            lval = left
        if isnumber(right):
             rval = float(right)
        else:
            rval = right
        # if we can do regular addition, do that
        if (isnumber(lval) and isnumber(rval)) or (isinstance(lval,list) and isinstance(rval, list)):
            return lval + rval
        # add a float to each thing in a list
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
                res[lval.index(i)] = self.doadd( res[lval.index(i)],rval)
            return res
        # else, do string addition
        else:
            return str(lval) + str(rval)

    # handles subtracting two things
    def dosubtract(self, left, right):
        # check if the things are numbers
        if isnumber(left):
            lval = float(left)
        else:
            lval = left
        if isnumber(right):
             rval = float(right)
        else:
            rval = right
        # if we can do normal subtraction, do that
        if (isnumber(lval) and isnumber(rval)) or (isinstance(lval,list) and isinstance(rval, list)):
            return lval - rval
        # handle subtracting from an array
        elif (isnumber(lval) and isinstance(rval, list)):
            res = list(rval)
            for i in rval:
                res[rval.index(i)] = self.dosubtract( res[rval.index(i)],lval)
            return res
        elif  (isinstance(lval, list) and isnumber(rval)):
            res = list(lval);
            for i in lval:
                res[lval.index(i)] = self.dosubtract( res[lval.index(i)],rval)
            return res
        #do string subtraction
        elif (isinstance(lval, str) or isinstance(rval, str)):
            res = str(str(lval).decode('string_escape').replace(str(rval).decode('string_escape'),""))
            return res
        # ehhh hopefully we don't get here
        else:
            # maybe i should throw some sort of error or something?
            return lval - rval

    # handle conconatinating two things
    def doconcat(self, left, right):
        lval = left
        rval = right
        #concat two numbers - 3 + 5 = 35
        if (isnumber(lval) and isnumber(rval)):
            return str(lval) + str(rval)
        # append a number/string to an array
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
        # append two arrays
        elif (isinstance(lval, list) and isinstance(rval, list)):
            return lval + rval
        else:
            return str(lval) + str(rval)

    # handle multiplication
    def domult(self, left, right):
        lval = left
        rval = right
        # normal multiplication
        if isnumber(lval) and isnumber(rval):
            return lval * rval
        # multiply all things in an array by a thing
        elif (isnumber(lval) and isinstance(rval, list)):
            res = list(rval)
            for i in rval:
                res[rval.index(i)] = self.domult(res[rval.index(i)], lval)
            return res
        elif  (isinstance(lval, list) and isnumber(rval)):
            res = list(lval);
            for i in lval:
                res[lval.index(i)] = self.domult(res[lval.index(i)],rval)
            return res
        # multiply by a string i guess
        elif isnumber(lval):
            res =  int(lval) * rval
            return res
        elif isnumber(rval):
            res =  lval * int(rval)
            return res

    # handle division
    def dodiv(self, lval, rval):
        #float division
        if isnumber(lval) and isnumber(rval):
            try:
                res = float(lval)/float(rval)
                return res
            except ZeroDivisionError:
                return 0.0
        #array/float division
        elif isinstance(rval,list):
            res = list(rval)
            for i in rval:
                res[rval.index(i)] = self.dodiv(lval,res[rval.index(i)])
            return res
        elif  (isinstance(lval, list)):
            res = list(lval)
            for i in lval:
                res[lval.index(i)] = self.dodiv(res[lval.index(i)], rval)
            return res
        #subdivide a string;
        elif (isinstance(lval,str) and isnumber(rval)):
            strlen = len(lval)
            chunkamt = int(round(strlen / rval))
            if (chunkamt <= 0):
                chunkamt = 1;
            res = list(chunkstring(str(lval), chunkamt))
            return res
        elif (isinstance(lval,str) and isinstance(rval,str)):
            if rval != "":
                res = list(lval.decode('string_escape').split(rval.decode('string_escape')))
            else:
                res = lval
            return res
        #uhh you shouldn't divide by a string so let's return 0
        elif (isinstance(rval,str)):
            return 0.0
        #hope we don't get here lol
        else:
            return lval/rval;

    # visit a binary operator
    def visit_BinOp(self, node):
        res = 0
        if self.verbose: print "trying binaryop node " + str(node.op)
        # do basic adding/concatinating
        if node.op.type == PLUS:
            res = self.doadd(self.visit(node.left), self.visit(node.right))
        elif node.op.type == CONCAT:
            res = self.doconcat(self.visit(node.left), self.visit(node.right))
        # call another function
        elif node.op.type == CALL:
            if self.verbose: print "interpreting a call " + str(node.left)
            return self.dofunc(node.left.value, node.right.value)
        # some more math
        elif node.op.type == MINUS:
            res = self.dosubtract(self.visit(node.left), self.visit(node.right))
        elif node.op.type == MUL:
            res = self.domult(self.visit(node.left),self.visit( node.right))
        elif node.op.type == DIV:
            res = self.dodiv(self.visit(node.left), self.visit(node.right))
        elif node.op.type == EXPONENT:
            res =  pow(self.visit(node.left),self.visit(node.right))
        # get the value at an index of an array
        elif node.op.type == INDEX:
            #if self.verbose: print "trying to interpret an array index " + node.left.value + "[" + str(int(node.right)) + "]"
            arr = self.visit(node.left)
            if isnumber(node.right):
                index = int(node.right)
            elif isinstance(node.right, str):
                index = self.vars[node.right]
            # if the array isn't that long, return 0
            if arr == 0:
                return 0.0;
            if float(index) >= len(arr):
                res = 0.0
            else:
                # return the array item
                if (isinstance(arr,unicode)):
                    arr = ast.literal_eval(arr);
                res = arr[int(index)]
        # evaluate conditionals
        elif node.op.type == EQUALS:
            res = (self.visit(node.left) == self.visit(node.right))
            if (res):
                res = 1
            else:
                res = 0
        elif node.op.type == NOTEQ:
            res = (self.visit(node.left) != self.visit(node.right))
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
        # handle file output
        elif node.op.type == FILEOUT:
            # check if filename is a variable
            if not isinstance(node.left, Var):
                fname = node.left.value
            else:
                fname = self.vars[node.left.value]
            # write to the file
            f = open(fname, "w")
            text = self.visit(node.right)
            f.write(text)
            f.close()
            return text;
        if self.verbose: print "computed binaryop node " + str(node.op)
        if self.verbose: print "result: " + str(res)
        return res

    # handle conditional nodes
    def visit_CondOp(self, node):
        res = 0;
        if self.verbose: print "trying conditional node "
        # nonzero = true, zero = false
        if (self.visit(node.cond) != 0):
            res = self.visit(node.thendo)
        else:
            res = self.visit(node.elsedo)
        return res;

    # handle while loops
    def visit_LoopOp(self, node):
        res = 0;
        if self.verbose: print "trying while loop"
        while(self.visit(node.cond) != 0):
            res = self.visit(node.thendo)
        return res;

    # if it's just a numnber, return that
    def visit_Num(self, node):
        return node.value

    # return a string, doing format mapping
    def visit_String(self, node):
        res = node.value
        if self.verbose: print self.vars
        res = format_map(res, self.vars)
        return res

    # return an array
    def visit_Array(self, node):
        res = list(node.value)
        # evaluate any variables in the array
        for s in node.value:
            if isinstance(s,basestring):
                try:
                    res[node.value.index(s)] = format_map(s, self.vars)
                    var = res[node.value.index(s)]
                    if islist(var):
                        res[node.value.index(s)] = var
                except KeyError as e:
                    return res;
        return res

    # code for calling another function
    def dofunc(self,function,passargs=None):
        function = function.strip('"')
        function = function.strip("'")
        if self.verbose: print "calling a function " +function
        funname = function
        funnode = self.funcs.get(funname)
        #see if the function exists, otherwise return 0
        if funnode == None:
            funnode = self.funcs.get(self.vars.get(funname))
        if funnode == None:
            return 0.0
        # evaluate the passed arguments
        argv = passargs
        if isinstance(argv,str) and argv[0].isalpha and argv[0] not in ('"', "'"):
            argv = self.vars[argv]
        elif isinstance(argv, str) and argv[0] in ('"', "'"):
            argv = argv[1:-1]
        previous = None
        # save the previous call's argv
        # adapted from munificent's solution
        # https://www.reddit.com/r/ProgrammingLanguages/comments/5vemme/working_on_my_own_simple_interpreted_language/de2fla9/
        if (self.funcargs.get(funnode) != None):
            previous = self.funcargs[funnode]
        # store them in the funcargs dictionary
        self.funcargs[funnode] = argv
        self.vars["argv"] = self.funcargs[funnode]
        # visit the function and return the result
        res = self.visit(funnode)
        # restore the outer call's argv
        if self.verbose: print ("attempting to restore: " + str(previous))
        self.funcargs[funnode] = previous
        self.vars['argv'] = previous
        if self.verbose: print ("attempting to return: " + str(res))
        return res

    # interpret the code
    def interpret(self, args, fileloc):
        # store the file location in the fileloc
        self.fileloc = fileloc + "/"
        self.vars['fileloc'] = self.fileloc
        # get the list of cuntions
        funcs = self.parser.parse()
        self.funcs = funcs
        if self.verbose: print funcs;
        if funcs is None:
            print "Error: No functions found in file."
            return 0
        if "main" not in funcs:
            print "Error: No main function found in file."
            return 0
        if self.verbose: print "storing " + str(args) + " in " + str(funcs['main'])
        # put command line args as the argv for main
        self.funcargs[funcs['main']] = args
        # visit the main function
        if not self.parser.tokens:
            self.dofunc('main', args)

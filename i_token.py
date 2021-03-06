# Tokens are the very small bits of data that the source code is broken down into.

#token types
FLOAT, PLUS, MINUS, MUL, DIV, EOF = 'FLOAT', 'PLUS', 'MINUS', 'MUL', 'DIV', 'EOF'
LPAREN, RPAREN = '(', ')'
LBRACKET, RBRACKET = '{', '}'
LSQUARE, RSQUARE = '[', ']'
EQUALS = "=="
NOTEQ = "!="
GREATER = ">"
LESSER = "<"
GREATEREQ = ">="
LESSEREQ = "<="
SEMI = ';'
CONCAT = "."
ASSIGN = "="
ARRASSIGN = "=a="
ID = "ID"
COMMA = "COMMA"
EXPONENT = "EXPONENT"
PRINT = "PRINT"
COND = "COND"
THENDO = "THENDO"
ELSEDO = "ELSEDO"
FUNCTION = "FUNCTION"
CALL = "CALL"
STRING = "STRING"
ARRAY = "ARRAY"
PROMPT = "PROMPT"
FILEIN = "FILEIN"
FILEOUT = "FILEOUT"
RANDOM = "RANDOM"
RETURN = "RETURN"
INDEX = "INDEX"
WHILE = "WHILE"
LEN = "LEN"
FLOOR = "FLOOR"

# here is the Token class
class Token(object):
    # each token has a type and a value
    def __init__(self,mtype, mvalue, lc=0):
        self.type = mtype
        self.value = mvalue
        self.linecount = lc

    #when you debug, you can print out a token
    def __str__(self):
        return 'Token({type}, {value})'.format(type=self.type,value=repr(self.value))

    def __repr__(self):
        return self.__str__()

# ahh, the lexer
# this breaks the source code down into tokens
# the tokens are then used by the parser

from i_token import *

#these are parsed as functions or whatever instead of as variable names
RESERVED_KEYWORDS = {
'print':Token('PRINT','PRINT'),
'fun':Token('FUNCTION','FUNCTION'),
'if':Token("COND","COND"),
'while':Token("WHILE","WHILE"),
'then':Token("THENDO","THENDO"),
'else':Token("ELSEDO","ELSEDO"),
'call':Token("CALL","CALL"),
'prompt':Token("PROMPT","PROMPT"),
'return':Token("RETURN","RETURN"),
'filein':Token("FILEIN","FILEIN"),
'fileout':Token("FILEOUT","FILEOUT"),
'random':Token("RANDOM","RANDOM"),
'len':Token("LEN","LEN"),
'floor':Token("FLOOR","FLOOR")
}

# the lexer reads through the source code
class Lexer(object):
    def __init__(self, text, verbose):
        self.text = text;
        # start at the beginning
        self.pos = 0
        self.current_char = self.text[self.pos]
        #if we are verbose, you'll get Lots of debug messages lol
        self.verbose = verbose

    # maybe some day i'll add in real error handling lol lol
    def error(self, errortext):
        raise Exception("Invalid character: " + errortext)

    # peek ahead at the next character
    # useful for determining what comes next
    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    # move forward one character in the source code
    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    # skip over anything until you get to another pound sign
    # yay block comments
    def skip_comment(self):
        while self.current_char != '#':
            self.advance()
        self.advance()

    # just skip that whitespace
    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    # scan in a STRING!!!
    # quotetype refers to the quote that started the string
    # that way you can have a single quote in a string defined by double quotes
    def lexSTRING(self,quotetype):
        self.advance()
        result = ''
        while self.current_char is not None and self.current_char != quotetype:
            result += self.current_char
            self.advance()
        # hey look here's some debugging
        if self.verbose: print result
        self.advance()
        return result

    # scan in an ARRAY!!!
    def lexARRAY(self):
        self.advance()
        result = []
        #loop through, processing each kind of item
        while self.current_char is not ']':
            # if it's a string, scan that
            if self.current_char in ("'",'"'):
                item = self.lexSTRING(self.current_char)
            # if it's an array in an aray, well, then, scan that
            elif self.current_char == '[':
                item = self.lexARRAY()
            # handle negative numbers
            elif self.current_char == '-':
                self.advance()
                item = 0-float(self.get_next_token().value)
            # just read in the next token
            elif self.current_char.isalnum():
                item = self.get_next_token().value
            # if it's something else, variable that.
            else:
                item = "{" + self.get_next_token().value + "}"
            if self.current_char == ",":
                self.advance()
            result.append(item)
        # advance over the ending bracket
        self.advance()
        return result

    # scan in a FLOAT!
    def lexFLOAT(self):
        result = ''
        # get the whole number part - scanning as a string for now
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        # if there's a decimal, handle that
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while (
                self.current_char is not None and
                self.current_char.isdigit()
            ):
                result += self.current_char
                self.advance()
        if self.verbose: print "lexfloating " + result
        # cast that string as a float
        return float(result)

    # parse in something that is either a variable or a function
    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        if self.verbose: print "id parsed: " + result
        # chck to see if it s a reserved function, otherwise just return an ID
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    # read in the next token
    def get_next_token(self):
        while self.current_char is not None:
            # handle comment skipping
            if self.current_char == "#":
                self.advance()
                self.skip_comment()
                continue
            # handle whitespace skipping
            if self.current_char.isspace():
                self.skip_whitespace()
                continue
            # scan brackets (for variable substitution in strings)
            if self.current_char == "{":
                self.advance()
                return Token(LBRACKET, '{')
            if self.current_char == "}":
                self.advance()
                return Token(RBRACKET, '}')
            # scan strings
            if self.current_char == '"' or self.current_char == "'":
                return Token(STRING, self.lexSTRING(self.current_char))
            # scan variables / function names
            if self.current_char.isalpha():
                return self._id()
            # scan arrays
            if self.current_char == '[':
                return Token(ARRAY, self.lexARRAY())
            # scan floats
            if self.current_char.isdigit():
                return Token(FLOAT, self.lexFLOAT())
            # scan single =, used for assignment
            if self.current_char == "=" and (self.peek() != "="):
                self.advance()
                return Token(ASSIGN, "=")
            # scan ==, and other compairson operators
            elif self.current_char == "=" and (self.peek() == "="):
                self.advance()
                self.advance()
                return Token(EQUALS, "==")
            if self.current_char == ">" and (self.peek() != "="):
                self.advance()
                return Token(GREATER, ">")
            elif self.current_char == ">" and (self.peek() == "="):
                self.advance()
                self.advance()
                return Token(GREATEREQ, ">=")
            if self.current_char == "<" and (self.peek() != "="):
                self.advance()
                return Token(LESSER, "<")
            elif self.current_char == "<" and (self.peek() == "="):
                self.advance()
                self.advance()
                return Token(LESSEREQ, "<=")
            # scan a comma
            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')
            # scan a period, used to concat
            if self.current_char == '.':
                self.advance()
                return Token(CONCAT, '.')
            # scan a semicolon, used to end statements
            if self.current_char == ";":
                self.advance()
                return Token(SEMI, ';')
            #scan arithmatic operators
            if self.current_char == "+":
                self.advance()
                return Token(PLUS, "+")
            if self.current_char == "-":
                self.advance()
                return Token(MINUS, "-")
            if self.current_char == "*":
                self.advance()
                return Token(MUL, "*")
            if self.current_char == "/":
                self.advance()
                return Token(DIV, '/')
            if self.current_char == "^":
                self.advance()
                return Token(EXPONENT, '^')
            # scan parenthesis
            if self.current_char == "(":
                self.advance()
                return Token(LPAREN, '(')
            if self.current_char == ")":
                self.advance()
                return Token(RPAREN, ')')
            #if we don't know what we're scanning, throw an error
            self.error("unknown token " + self.current_char)
        # return the end of file
        return Token(EOF, None)

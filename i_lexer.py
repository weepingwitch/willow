from i_token import *

#these are parsed as functions or whatever instead of 
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
'random':Token("RANDOM","RANDOM")
}

class Lexer(object):
    def __init__(self, text, verbose):
        self.text = text.lower()
        self.pos = 0
        self.current_char = self.text[self.pos]
        self.verbose = verbose

    def error(self, errortext):
        raise Exception("Invalid character: " + errortext)

    def peek(self):
        peek_pos = self.pos + 1
        if peek_pos > len(self.text) - 1:
            return None
        else:
            return self.text[peek_pos]

    def advance(self):
        self.pos += 1
        if self.pos > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.pos]

    def skip_comment(self):
        while self.current_char != '#':
            self.advance()
        self.advance()

    def skip_whitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def lexSTRING(self,quotetype):
        self.advance()
        result = ''
        while self.current_char is not None and self.current_char != quotetype:
            result += self.current_char
            self.advance()
        if self.verbose: print result
        self.advance()
        return result

    def lexARRAY(self):
        self.advance()
        result = []
        while self.current_char is not ']':
            if self.current_char in ("'",'"'):
                item = self.lexSTRING(self.current_char)
            elif self.current_char == '[':
                item = self.lexARRAY()
            elif self.current_char == '-':
                self.advance()
                item = 0-float(self.get_next_token().value)
            elif self.current_char.isalnum():
                item = self.get_next_token().value
            else:
                item = "{" + self.get_next_token().value + "}"

            if self.current_char == ",":
                self.advance()
            result.append(item)
        self.advance()
        return result


    def lexFLOAT(self):
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        if self.current_char == '.':
            result += self.current_char
            self.advance()
            while (
                self.current_char is not None and
                self.current_char.isdigit()
            ):
                result += self.current_char
                self.advance()
        if self.verbose: print "lexfloating " + result;
        return float(result)

    def _id(self):
        result = ''
        while self.current_char is not None and self.current_char.isalnum():
            result += self.current_char
            self.advance()

        if self.verbose: print "id parsed: " + result
        token = RESERVED_KEYWORDS.get(result, Token(ID, result))
        return token

    def get_next_token(self):
        while self.current_char is not None:

            if self.current_char == "#":
                self.advance()
                self.skip_comment()
                continue

            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == "{":
                self.advance()
                return Token(LBRACKET, '{')

            if self.current_char == "}":
                self.advance()
                return Token(RBRACKET, '}')

            if self.current_char == '"' or self.current_char == "'":
                return Token(STRING, self.lexSTRING(self.current_char))

            if self.current_char.isalpha():
                return self._id()


            if self.current_char == '[':
                return Token(ARRAY, self.lexARRAY())

            if self.current_char.isdigit():
                return Token(FLOAT, self.lexFLOAT())


            if self.current_char == "=" and (self.peek() != "="):
                self.advance()
                return Token(ASSIGN, "=")

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

            if self.current_char == ',':
                self.advance()
                return Token(COMMA, ',')

            if self.current_char == '.':
                self.advance()
                return Token(CONCAT, '.')


            if self.current_char == ";":
                self.advance()
                return Token(SEMI, ';')

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

            if self.current_char == "(":
                self.advance()
                return Token(LPAREN, '(')

            if self.current_char == ")":
                self.advance()
                return Token(RPAREN, ')')








            self.error("unknown token " + self.current_char)
        return Token(EOF, None)

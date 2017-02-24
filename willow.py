#!/usr/bin/env python
import sys, argparse, os, string
from i_interpreter import *

# ok here's the part that reads in the source code
# and then calls the interpreter on it
def runscript(filename, verbose, args, tokens):
    if verbose: print args
    filename = filename.rstrip()
    # add in the extension if it's not there
    if not filename.endswith(".wlw"):
        filename = filename + ".wlw"
    # open and read the file
    f = open(filename, "U")
    text = f.read()
    # get the file location (so scripts can reference other files)
    fileloc = os.path.dirname(os.path.realpath(f.name))
    f.close()
    # pass the file and the arguments to the lexer, pass that to the parser,
    # and then pass that to the interpreter, and then interpret it!!
    Interpreter(Parser(Lexer(text, verbose, tokens, filename))).interpret(args, fileloc)


if __name__ == "__main__":
    # deal with command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    parser.add_argument("-t", "--tokens", help="output parsed tokens before execution",action="store_true")
    parser.add_argument("src", help="the script to interpret")
    parser.add_argument("pargs", nargs="*", help="arguments to pass to the script")
    args = parser.parse_args()
    # run the script
    runscript(args.src, args.verbose, args.pargs, args.tokens)

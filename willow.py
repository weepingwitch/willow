#!/usr/bin/env python
import sys, argparse, os
from i_interpreter import *

# ok here's the part that reads in the source code
# and then calls the interpreter on it
def runscript(filename, verbose, args):
    if verbose: print args
    filename = filename.rstrip()
    # add in the extension if it's not there
    if not filename.endswith(".wlw"):
        filename = filename + ".wlw"
    # open and read the file
    f = open(filename)
    text = f.read()
    fileloc = os.path.dirname(os.path.realpath(f.name))
    Interpreter(Parser(Lexer(text, verbose))).interpret(args, fileloc)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    parser.add_argument("src", help="the script to interpret")
    parser.add_argument("pargs", nargs="*", help="arguments to pass to the script")
    args = parser.parse_args()

    runscript(args.src, args.verbose, args.pargs)

#!/usr/bin/env python
import sys, argparse, os
from i_interpreter import *


def runscript(filename, verbose, args):
    if verbose: print args
    filename = filename.rstrip()
    if not filename.endswith(".wlw"):
        filename = filename + ".wlw"
    f = open(filename)
    text = f.read()
    Interpreter(Parser(Lexer(text, verbose))).interpret(args, os.path.dirname(os.path.realpath(f.name)))
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",action="store_true")
    parser.add_argument("src", help="the script to interpret")
    parser.add_argument("pargs", nargs="*", help="arguments to pass to the script")
    args = parser.parse_args()

    runscript(args.src, args.verbose, args.pargs)

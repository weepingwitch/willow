# willow
a (very simple) weakly-typed functional programming language / interpreter, built in python

## usage
regular usage:
```bash
python willow.py source_code.wlw
```

passing in command-line arguments:
```bash
python willow.py source_code.wlw myarg1 myarg2
```

## examples / test functions

```
fun main
{
  # a simple hello world function #
  mystring = "Hello, world!";
  print mystring;
}
```

for a more thorough suite of test functions, check out
[tests/test.wlw](https://github.com/weepingwitch/willow/blob/master/tests/test.wlw) which demonstrates some of the main features of the language

## influences
while the syntax/grammar/abilities of my language are mainly dictated by what i am able to figure out how to program, some of the functionality is inspired by my experiences with ti-basic, shell scripting, javascript, and python

the VERY beginning of the language was based off of [this tutorial](https://ruslanspivak.com/lsbasi-part1/) for creating a Pascal interpreter from scratch

however, i’ve made a Lot of changes to the actual language structure, and added a LOT that wasn’t covered in the tutorial (i.e. calling functions, conditionals, loops, input/output, etc.)


## variables

you don’t have to declare variables as being of a certain type

```
myvar = 5;
myvar = "hello!";
myvar = [2,3,4];
```

floats, strings, and arrays are the only variable types so far.

booleans kinda exist when evaluating conditionals… 0.0 evaluates to false and non-zero evaluates to true

you can reference an uninitialized variable, it just defaults to 0.0

all variables are currently global in scope, with the exception of the special variable sysargs (see below)

## basic arithmatic

you can add and subtract and multiply and divide!

you can also use ^ to do exponent

wow fun! it also follows order of operations yay

you can add different variable types too!

```
mystring = "hello";
mynum = 6;
mycombined = mystring + mynum;
print mycombined;  # should print "hello6.0" #
```

## functions

every program needs to have a main function, that is the function that is executed by the interpreter

the main function can call other functions

it is possible to pass a value to a function, which is then accessed by the special variable sysargs:

```
fun addtwo
{
  x = sysargs; # sysargs holds what was passed in below #
  x = x + 2;
  return x;
}

fun main{
  y = 5;
  z = call(addtwo)(y);
  print z; # should print 7.0 #
}

```

in the main function, sysargs returns the command line arguments supplied when the file was interpreted

functions can call themselves, allowing recursive programming!

```
#recursively print the factorial#
fun factorial{
  #sysargs holds the arguments passed to a function#
  x = sysargs;
  if (x == 1)
  then {
    return x;
  }
  else {
    if (x == 0)
    then{
     return 0;
    }
    else{
      y = x-1;
      z = x * call(factorial)(y);
      return z;
    };
  };
}

fun main{
  #sysargs holds the arguments passed to a function.
  in this case, it's the args from command line.
  adding 0 to treat it as a float,
  since it's read in from command line as string#
  num = sysargs[0] + 0;
  fact = call(factorial)(num);
  print "the factorial of " + num + " is " + fact;
}
```

## built-in functions
### conditional statements:
possible through this format:
```
if (condition)
then
{
  #thencode#
}
else
{
  #elsecode#
};
```
if condition evaluates to nonzero, thencode is run, if it evaluates to zero, elsecode is run

else is optional

### loops:

so far, i’ve just implemented a while loop

```
while (condition) then { #loopcode# };
```

### user input:

you can prompt the user to type in something at the command line

for instance:
```
myname = prompt(”What is your name?”);
print “Hello, “ + myname;
```

### file input/output:

you can read from and write to files!
```
myvar = “hello filesystem!”;
fileout(“myfile.txt”)(myvar);
filename = “myfile.txt”;
myresult = filein(filename);
print myresult;
```
the above code will write the text “hello filesystem!” to the file myfile.txt (located in the same directory as the willow script that is being interpreted), then read in the text and print it out.

### random number generation:

you can generate random floats by calling random(max_number) which will generate a float between 0 and max_number

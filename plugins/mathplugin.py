from .plugin import PlushiePlugin, plushieCmd, commandDoc

import math
import random
import re
from collections import namedtuple

Token = namedtuple("Token", ["type", "value"])
Symbol = namedtuple("Symbol", ["args", "operation", "type", "maxArgs"])
Op = namedtuple("Op", Symbol._fields + ("side", "precidence"))


_sine = Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.sin(a))
_cosine = Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.sin(a))
_tangent = Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.tan(a))
_log = Symbol(type="func", args=2, maxArgs=2, operation=lambda a, b: math.log(a, b))
_log10 = Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.log10(a))
_ln = Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.log(a))
_sqrt = Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.sqrt(a))
_base = Symbol(type="func", args=2, maxArgs=2, operation=lambda a, b: int(str(a), b))


# This function and the below taken from http://en.literateprograms.org/Fibonacci_numbers_%28Python%29
def powLF(n):
    if n == 1:
        return (1, 1)
    L, F = powLF(n//2)
    L, F = (L**2 + 5 * F**2) >> 1, L * F
    if n & 1:
        return ((L + 5 * F) >> 1, (L + F) >> 1)
    else:
        return (L, F)


def fib(n):
    return powLF(n)[1]


symbols = {
    # Ops
    "~": Op(type="op", args=1, maxArgs=1, side="right", precidence=3, operation=lambda a: ~a),
    "|": Op(type="op", args=2, maxArgs=2, side="left", precidence=4, operation=lambda a, b: a | b),
    "&": Op(type="op", args=2, maxArgs=2, side="left", precidence=5, operation=lambda a, b: a & b),
    "<<": Op(type="op", args=2, maxArgs=2, side="left", precidence=6, operation=lambda a, b: a << b),
    ">>": Op(type="op", args=2, maxArgs=2, side="left", precidence=6, operation=lambda a, b: a >> b),
    "+": Op(type="op", args=2, maxArgs=2, side="left", precidence=7, operation=lambda a, b: a + b),
    "-": Op(type="op", args=2, maxArgs=2, side="left", precidence=7, operation=lambda a, b: a - b),
    "*": Op(type="op", args=2, maxArgs=2, side="left", precidence=8, operation=lambda a, b: a * b),
    "/": Op(type="op", args=2, maxArgs=2, side="left", precidence=8, operation=lambda a, b: a / b),
    "%": Op(type="op", args=2, maxArgs=2, side="left", precidence=8, operation=lambda a, b: math.fmod(a, b)),
    "^": Op(type="op", args=2, maxArgs=2, side="right", precidence=9, operation=lambda a, b: math.pow(a, b)),
    "!": Op(type="op", args=1, maxArgs=1, side="right", precidence=10, operation=lambda a: math.factorial(a)),
    # NOTE: This replaces the - and + for their unary use
    "--": Op(type="flop", args=1, maxArgs=1, side="right", precidence=11, operation=lambda a: -a),
    "++": Op(type="flop", args=1, maxArgs=1, side="right", precidence=11, operation=lambda a: a),
    # Functions
    "sine": _sine,
    "sin": _sine,
    "cosine": _cosine,
    "cos": _cosine,
    "tangent": _tangent,
    "tan": _tangent,
    "log": _log,
    "log10": _log10,
    "ln": _ln,
    "sqrt": _sqrt,
    "base": _base,
    "deg": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.degrees(a)),
    "rad": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.radians(a)),
    "abs": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.fabs(a)),
    "floor": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.floor(a)),
    "ceil": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: math.ceil(a)),
    "round": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: round(a)),
    "roundto": Symbol(type="func", args=2, maxArgs=2, operation=lambda a, b: round(a, b)),
    "fib": Symbol(type="func", args=1, maxArgs=1, operation=lambda a: fib(a)),
    "rand": Symbol(type="func", args=2, maxArgs=2, operation=lambda a, b: random.uniform(a, b)),
    # Constants
    "pi": Symbol(type="const", args=0, maxArgs=0, operation=lambda: math.pi),
    "e": Symbol(type="const", args=0, maxArgs=0, operation=lambda: math.e)
}


class MathPlugin(PlushiePlugin):
    name = "Math Plugin"
    description = "Provides some mathematical understanding to Plushie"
    author = ["Garth"]

    @plushieCmd("calc")
    @commandDoc(extra="<expression>", doc="Returns the evaluation of <expression>")
    def calc(self, ctx, msg):
        args = msg.noCmdMsg()
        try:
            rpn = self.shunt(args)
            res = self.evalRPN(rpn)
            reply = "Answer is: {:g}".format(res)
        except RuntimeError as e:
            reply = e.args[0]
        except OverflowError:  # This only happens with the fib() function
            reply = "Resulting value is too large."
        ctx.msg(reply, msg.replyTo)

    @plushieCmd("bcalc")
    @commandDoc(extra="<expression>", doc="Returns the evaluation of <expression> in binary")
    def bcalc(self, ctx, msg):
        args = msg.noCmdMsg()
        try:
            rpn = self.shunt(args)
            res = self.evalRPN(rpn)
            reply = "Answer is: {0:#b}".format(res)
        except RuntimeError as e:
            reply = e.args[0]
        except OverflowError:  # This only happens with the fib() function
            reply = "Resulting value is too large."
        ctx.msg(reply, msg.replyTo)

    @plushieCmd("shunt", "rpn")
    @commandDoc(extra="<expression>", doc="Returns <expression> in infix notation")
    def shuntCmd(self, ctx, msg):
        args = msg.noCmdMsg()
        try:
            res = self.shunt(args)
            reply = " ".join(str(s) for s in res)
        except RuntimeError as e:
            print(e)
            reply = e.args[0]
        ctx.msg(reply, msg.replyTo)

    # This is based on Dijkstra's Shunting-yard Algorithm
    def shunt(self, string):
        output = []
        # NOTE: This holds Token's, not the raw values!
        stack = []
        # The '-' character can actually mean either the binary subtract operator or the unary negate operator.
        # To find out which it is, we use the fact that a binary operator can not show up right after another
        # operator or a left parenthesis.
        # This means I have to keep track of the previous token
        previousToken = None
        try:
            for token in self.tokenize(string):
                # Add numbers to output queue
                if token.type == "BINNUM":
                    val = int(token.value, 2)
                    output.append(val)
                if token.type == "HEXNUM":
                    val = int(token.value, 16)
                    output.append(val)
                if token.type == "NUMBER":
                    # Clear all space so negatives are properly connected
                    compressedVal = token.value.replace(" ", "").replace("\t", "")
                    # Coax the number into a correct value
                    if "." in compressedVal:
                        val = float(compressedVal)
                    else:
                        val = int(compressedVal)
                    output.append(val)
                # Handle functions
                elif token.type == "FUNC":
                    # Check for constants
                    if token.value in ["pi", "e"]:
                        output.append(token.value)
                    else:
                        stack.append(token)
                elif token.type == "SEP":
                    stackEnd = stack[-1:]
                    while stackEnd:
                        seVal = stackEnd[0].value
                        if seVal == "(":
                            break
                        else:
                            output.append(stack.pop().value)
                            try:
                                stackEnd = [stack[-1]]
                            except IndexError:
                                raise RuntimeError("Unmatched parentheses")
                # Handle operator precidence
                elif token.type == "OP":
                    if token.value not in symbols or symbols[token.value].type != "op":
                        raise RuntimeError("Undefined operator {:s}!".format(token.value))
                    # Check to see if the negative is unary, if it is set it as _
                    # Binary can have no op or left paren to its left, so check for that
                    if (token.value == "-" or token.value == "+") and (not previousToken or
                                                                       (previousToken.type == "OP" or
                                                                        previousToken.type == "LPAREN")):
                        # NOTE: Kind of a hack, for the unary I just double the operator.
                        currentOp = symbols[token.value*2]
                    else:
                        currentOp = symbols[token.value]
                    stackEnd = stack[-1:]
                    while stackEnd:
                        seVal = stackEnd[0].value
                        # Only pop operators off the stack
                        if seVal not in symbols or (symbols[seVal].type != "op" and symbols[seVal].type != "flop"):
                            break
                        prevOp = symbols[seVal]
                        if (currentOp.side == "left" and prevOp.precidence == currentOp.precidence or
                           currentOp.precidence < prevOp.precidence):
                                output.append(stack.pop().value)
                                stackEnd = stack[-1:]
                        else:
                            break
                    # Recreate token for unary - (messy, but it works)
                    if currentOp.type == "flop":
                        # For the value setting, see the note about setting currentOp
                        token = Token(type="OP", value=token.value*2)
                    stack.append(token)
                # Handle left parenthesis
                elif token.type == "LPAREN":
                    stack.append(token)
                elif token.type == "RPAREN":
                    stackEnd = stack[-1:]
                    # Remove everything up to the opening paren
                    while stackEnd and stackEnd[0].value != "(":
                        output.append(stack.pop().value)
                        try:
                            stackEnd = [stack[-1]]
                        except IndexError:
                            raise RuntimeError("Unmatched parentheses.")
                    # Get rid of the opening parentheses
                    try:
                        stack.pop()
                    except IndexError:
                        raise RuntimeError("Unmatched parentheses.")
                    # The the last thing is a function name, then add that to the output
                    if stack[-1:] and stack[-1:][0].type == "FUNC":
                        output.append(stack.pop().value)
                previousToken = token
            # Pop remaining ops into the stack
            lastop = stack[-1:]
            while lastop:
                curr = stack.pop().value
                if curr == ")" or curr == "(":
                    raise RuntimeError("Unmatched parentheses!")
                output.append(curr)
                lastop = stack[-1:]
        except RuntimeError:
            raise
        return output

    def tokenize(self, string):
        tokens = [
            ('BINNUM', r'0b[0-1]*'),
            ('HEXNUM', r'0x[0-9a-fA-F]*'),
            ('NUMBER', r'\d+(\.\d*)?'),
            ('OP',     r'(\>{2}|\<{2}|[\+\/\-\^\%\!\*\&\|\~])'),  # TODO: Generate this using the symbols that are ops
            ('NOOP',   r'[ \t]'),
            ('FUNC',   r'[A-Za-z]+[A-Za-z0-9]?'),
            ('SEP',    r','),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)')
        ]
        token_reg = '|'.join('(?P<%s>%s)' % pair for pair in tokens)
        get_tokens = re.compile(token_reg).match
        pos = 0
        mo = get_tokens(string)
        while mo is not None:
            typ = mo.lastgroup
            if typ != "NOOP":
                val = mo.group(typ)
                if typ == "FUNC":
                    val = val.lower()
                yield Token(typ, val)
            pos = mo.end()
            mo = get_tokens(string, pos)
        if pos != len(string):
            raise RuntimeError("Unexpected character '{:s}'.".format(string[pos]))

    def evalRPN(self, rpn):
        stack = []
        for token in rpn:
            # Strings are ops and functions
            if isinstance(token, str):
                if token in symbols:
                    funcType = symbols[token]
                    argStack = []
                    # Attempt to get the appropiate number of arguments
                    try:
                        for i in range(funcType.args):
                            argStack.append(stack.pop())
                    except IndexError:
                        raise RuntimeError("Incorrect number of arguments for operator or function: {:s}".format(token))
                    # Do the calculation
                    try:
                        result = funcType.operation(*reversed(argStack))
                    except OverflowError:
                        raise RuntimeError("Result of function is too large to compute.")
                    except ZeroDivisionError:
                        raise RuntimeError("Cannot divide by zero!")
                    except ValueError:
                        raise RuntimeError("Resulting value is no longer calculable by PlushieBot (either imaginary, "
                                           "undefined, or an edge case).")
                    stack.append(result)
                else:
                    raise RuntimeError("Unknown function or operator {:s}".format(token))
            else:
                # Numbers are already either an int or float type
                stack.append(token)

        if len(stack) == 1:
            return stack.pop()
        else:
            raise RuntimeError("Bad stack! (You've likely added an extra parameter somewhere)")

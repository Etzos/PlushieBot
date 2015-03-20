import os
import sys
import termios
import tty


class TermUtil:
    @staticmethod
    def getPos(stdin=sys.stdin):
        fd = stdin.fileno()
        old = termios.tcgetattr(fd)

        tty.setraw(fd)
        sys.stdout.write("\033[6n")

        existing = currentChar = ""

        try:
            while currentChar != "R":
                existing += currentChar
                currentChar = stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)

        return tuple([int(i) for i in existing[2:].split(';')])

    @staticmethod
    def getLine(stdin=sys.stdin):
        fd = stdin.fileno()
        old = termios.tcgetattr(fd)

        line = ""
        try:
            tty.setraw(fd)
            line = stdin.readline()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
        return line

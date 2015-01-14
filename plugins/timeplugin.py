from .plugin import *

import time


class TimePlugin(PlushiePlugin):
    name = "Time Plugin"
    description = "I'll tell you the current time"
    authors = ["Garth"]

    @plushieCmd("time")
    def run(self, ctx, msg):
        ctx.msg("It is " +
                 time.strftime("%A, %d %B %Y %I:%M:%S %p (%Z)",
                               time.localtime()),
                 msg.replyTo)

from .plugin import *

import random


class KickPlugin(PlushiePlugin):
    name = "Kick Plugin"
    description = "Make Plushie kick someone"
    authors = ["Garth"]

    @plushieCmd("kick")
    @commandDoc(extra="<thing to kick>", doc="Has Plushie kick <things to kick>")
    def run(self, ctx, msg):
        target = msg.getArgs()
        rand = random.randint(1, 10)

        if not target or target[0] == "":
            ctx.msg("/me attempts to kick the air... And misses")
        elif rand > 8:
            ctx.msg("/me kicks " + target[0] + " -- Ouch!")
        else:
            ctx.msg("/me kicks " + target[0] + " -- A softer kick than expected")

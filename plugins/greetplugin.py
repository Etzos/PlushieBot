from .plugin import *


class GreetPlugin(PlushiePlugin):
    name = "Greeting Plugin"
    description = "Greet a player"
    authors = ["Garth"]

    @plushieCmd("greet")
    @commandDoc(extra="<player>", doc="Has Plushie greet <player>")
    def run(self, ctx, msg):
        target = msg.getArgs()

        if target[0] == "":
            ctx.msg("I don't know who to greet.", msg.replyTo)
        else:
            ctx.msg("Yay! " + target[0] + " is here! \\ :O / Hi " + target[0] + "!")

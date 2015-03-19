from .plugin import *


class StabPlugin(PlushiePlugin):
    name = "Stab Plugin"
    description = "Make Plushie attempt to stab a player"
    authors = ["Garth"]

    @plushieCmd("stab")
    @commandDoc(extra="<item name>", doc="Has Plushie stab <item name>")
    def run(self, ctx, msg):
        target = msg.getArgs()

        if target[0] == "":
            ctx.msg("I don't know who to stab", msg.replyTo)
        elif target[0] == "Garth":
            ctx.msg("Why would I ever stab Garth? He's too nice for me to do such a thing.", msg.replyTo)
        else:
            ctx.msg("/me glomps " + target[0])
            ctx.msg("And you thought I was going to stab you. :P", target[0])

from .plugin import *


class SayPlugin(PlushiePlugin):
    name = "Say Plugin"
    description = "Make me say something (only usable by certain people)"
    authors = ["Garth"]

    @plushieCmd("say")
    @commandDoc(extra="<things for Plushie to say>", doc="Has Plushie say <things for Plushie to say>")
    def run(self, ctx, msg):
        if msg.player == "Garth":
            ctx.msg(msg.noCmdMsg())
            return
        elif msg.player == "WhiteKitsune":
            ctx.msg("/msg Garth WhiteKitsune is telling me to say: {:s}".format(msg.noCmdMsg()))
            ctx.msg(msg.noCmdMsg())
        else:
            ctx.msg("/me bops {:s} on the head -- Don't pull my strings! d.b".format(msg.player))

from .plugin import PlushiePlugin, plushieCmd, commandDoc


class SayPlugin(PlushiePlugin):
    name = "Say Plugin"
    description = "Make me say something (only usable by certain people)"
    authors = ["Garth"]

    @plushieCmd("say")
    @commandDoc(extra="<things for Plushie to say>", doc="Has Plushie say <things for Plushie to say>")
    def run(self, ctx, msg):
        if msg.player == "Garth" or "WhiteKitsune":
            ctx.msg(msg.noCmdMsg())
            return
        else:
            ctx.msg("/me bops {:s} on the head -- Don't pull my strings! d.b".format(msg.player))

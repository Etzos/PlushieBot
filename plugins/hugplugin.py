from .plugin import *


class HugPlugin(PlushiePlugin):
    name = "Hugging plugin"
    description = "Hug someone!"
    authors = ["Garth"]

    @plushieCmd("hug")
    def run(self, ctx, msg):
        target = msg.getArgs()
        if not target or target[0].lower() == "plushie":
            ctx.msg("/hug his soft plushie self")
        elif target[0].lower() == "garth":
            if msg.player.lower() == "athena":
                ctx.msg("/hug Garth (on Athena's behalf)")
            else:
                ctx.msg("I'm not going to hug Garth. " +
                        "He stabs me when I do that.",
                        msg.replyTo)
        else:
            ctx.msg("/hug {:s}".format(target[0]))

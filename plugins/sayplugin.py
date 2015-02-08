from .plugin import *


class SayPlugin(PlushiePlugin):
    name = "Say Plugin"
    description = "Make me say something (only usable by certain people)"
    authors = ["Garth"]

    @plushieCmd("say")
    def run(self, ctx, msg):
        if msg.player == "Garth":
            ctx.msg(msg.noCmdMsg())
        if msg.player == "WhiteKitsune":
            ctx.msg("Garth!! WhiteKitsune is telling me to say things 9.9")

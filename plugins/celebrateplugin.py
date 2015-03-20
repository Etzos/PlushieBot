from .plugin import PlushiePlugin, plushieCmd, commandDoc

import random


class CelebratePlugin(PlushiePlugin):
    name = "Celebration Plugin"
    description = "Give Plushie some awesome celebration lines"
    authors = ["Garth", "Zarda"]

    @plushieCmd("celebrate")
    @commandDoc(doc="Has Plushie celebrate")
    def celebrate(self, ctx, msg):
        rand = random.randint(0, 4)

        if rand == 0:
            ctx.msg("WooOOooOOooOOooOOoo! Party! \\ :O /", msg.replyTo)
        elif rand == 1:
            ctx.msg("It's time to celebrate everyone! ~(^.^~)", msg.replyTo)
        elif rand == 2:
            ctx.msg("\\(^.^)/ Get happy: celebrate!", msg.replyTo)
        elif rand == 3:
            ctx.msg("Who is ready to partaaaaayyy!", msg.replyTo)
        else:
            ctx.msg("(~^.^)~ Party time! ~(^.^~)", msg.replyTo)

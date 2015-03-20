from .plugin import PlushiePlugin, plushieCmd, commandDoc

import random


class PingPlugin(PlushiePlugin):
    name = "Ping"
    description = "Respond to a player's ping"
    authors = ["Garth"]

    @plushieCmd("ping")
    @commandDoc(doc="Responds to a player's ping")
    def run(self, ctx, msg):
        rand = random.randint(1, 10)
        if msg.isWhisper or rand < 8:
            ctx.msg(msg.player + ": Pong!", msg.replyTo)
        else:
            ctx.msg("/me drops the ping pong ball")

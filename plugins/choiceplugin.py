from .plugin import PlushiePlugin, plushieCmd, commandDoc

import random


class ChoicePlugin(PlushiePlugin):
    name = "Choice Plugin"
    description = "Make Plushie pick an item from a comma-separated list"
    authors = ["Garth"]

    @plushieCmd("choice", "choose", "pick")
    @commandDoc(extra="<list of things to choose from>",
                doc="Returns a single choice from a list of choices. Use a comma and a space to separate the choices")
    def run(self, ctx, msg):
        options = msg.noCmdMsg().split(", ")
        optlen = len(options)

        if optlen < 1:
            ctx.msg("You didn't give me anything to choose from!", msg.replyTo)
        if optlen < 2:
            ctx.msg("Looks like I don't have a choice, so " +
                    "I choose '" + options[0] + "'!", msg.replyTo)
        else:
            ctx.msg("I pick '" + random.choice(options).strip() + "'", msg.replyTo)

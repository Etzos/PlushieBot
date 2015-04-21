from .plugin import PlushiePlugin, plushieCmd, commandDoc

import random


class RandomPlugin(PlushiePlugin):
    name = "Random Plugin"
    description = "A plugin for various things that rely on randomness."
    authors = ["Garth", "Zarda"]

    @plushieCmd("choice", "choose", "pick")
    @commandDoc(extra="<list of things to choose from>",
                doc="Returns a single choice from a list of choices. Use a comma and a space to separate the choices")
    def choice(self, ctx, msg):
        options = msg.noCmdMsg().split(", ")
        optlen = len(options)

        if optlen < 1:
            ctx.msg("You didn't give me anything to choose from!", msg.replyTo)
        if optlen < 2:
            ctx.msg("Looks like I don't have a choice, so " +
                    "I choose '" + options[0] + "'!", msg.replyTo)
        else:
            ctx.msg("I pick '" + random.choice(options).strip() + "'", msg.replyTo)

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

    @plushieCmd("doge")
    @commandDoc(doc="Everyone needs a little doge in their life!")
    def doge(self, ctx, msg):
        if msg.isWhisper:
            ctx.msg("Doge is for all to enjoy.")
            return
        setup = [
            "Much random: ",
            "Very link: ",
            "So doge: "
        ]
        links = [
            "http://i.imgur.com/nN62UTC.jpg",
            "http://i.imgur.com/q7P5DZO.png",
            "http://i.imgur.com/uI7qPj0.png",
            "http://i.imgur.com/V7lvFhb.jpg",
            "http://i.imgur.com/Uii10VW.jpg",
            "http://i.imgur.com/mI3GSW5.jpg",
            "http://i.imgur.com/MWQBwjQ.jpg",
            "http://i.imgur.com/HMyhGAF.jpg",
            "http://i.imgur.com/JFbSzXx.jpg",
            "http://i.imgur.com/JUZV8nb.jpg",
            "http://i.imgur.com/bDNGTjb.jpg",
            "http://i.imgur.com/7oacJiW.jpg"
        ]
        ctx.msg(random.choice(setup) + random.choice(links))

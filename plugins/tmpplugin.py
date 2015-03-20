from .plugin import PlushiePlugin, plushieCmd, commandDoc


class TmpPlugin(PlushiePlugin):
    name = "Temporary Plugin"
    description = "Doesn't do a whole lot honestly"
    authors = ["Etzos"]

    @plushieCmd("crazy")
    @commandDoc(extra="<item name>", doc="Has Plushie say <item name> is crazy")
    def run(self, ctx, msg):
        ctx.msg("Yep {:s} is crazy".format(msg.noCmdMsg()), msg.replyTo)

#    @plushieCmd("load")
#    def loadPlugin(self, ctx, msg):
#        ctx.parent.registerPluginFromString("celebrateplugin.CelebratePlugin")
#        ctx.msg("Attempted to load plugin.", msg.replyTo)

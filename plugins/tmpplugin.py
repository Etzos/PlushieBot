from .plugin import *


class TmpPlugin(PlushiePlugin):
    name = "Temporary Plugin"
    description = "Doesn't do a whole lot honestly"
    authors = ["Etzos"]
    
    @plushieCmd("crazy")
    def run(self, ctx, msg):
        ctx.msg("Yep %s is crazy" % (msg.noCmdMsg(),), msg.replyTo)

#    @plushieCmd("load")
#    def loadPlugin(self, ctx, msg):
#        ctx.parent.registerPluginFromString("celebrateplugin.CelebratePlugin")
#        ctx.msg("Attempted to load plugin.", msg.replyTo)
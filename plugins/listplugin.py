from .plugin import *

class ListPlugin(PlushiePlugin):
    name = "List Plugins"
    description = "Lists all the available commands"
    authors = ["Garth"]

    @plushieCmd("list")
    def listCommands(self, ctx, msg):
        cmds = ctx.parent.commands
        ctx.msg("Available commands ({:d}): !{:s}".format(len(cmds), ", !".join(cmds.keys())), msg.replyTo)

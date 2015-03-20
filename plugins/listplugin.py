from .plugin import PlushiePlugin, plushieCmd, commandDoc


class ListPlugin(PlushiePlugin):
    name = "List Plugins"
    description = "Lists all the available commands"
    authors = ["Garth"]

    @plushieCmd("list")
    @commandDoc(doc="Lists all commands that Plushie can understand")
    def listCommands(self, ctx, msg):
        cmds = ctx.parent.commands
        ctx.msg("Available commands ({:d}): !{:s}".format(len(cmds), ", !".join(sorted(cmds.keys()))), msg.replyTo)

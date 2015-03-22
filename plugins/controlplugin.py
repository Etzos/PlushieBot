from .plugin import PlushiePlugin, plushieCmd, commandDoc


class ControlPlugin(PlushiePlugin):
    name = "Control Plugin"
    description = "Control the Plushie!"
    authors = ["Garth"]

    @plushieCmd("reload")
    def control(self, ctx, msg):
        if msg.player != "Garth":
            ctx.msg("{:s}: You do not have permission to reload plugins.".format(msg.player), msg.replyTo)
            return
        plugin_name = " ".join(msg.getArgs())

        worked = ctx.parent.reload_plugin(plugin_name)
        if worked:
            ctx.msg("'{:s}' plugin reloaded.".format(plugin_name))
        else:
            ctx.msg("Reload of '{:s}' plugin failed.".format(plugin_name), msg.replyTo)

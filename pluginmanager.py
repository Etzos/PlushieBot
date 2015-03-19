# TODO: Wrap the tick and message methods in try/except clauses to prevent killing the thread
# TODO: When that's done, remember to disable the plugin, so it doesn't cause any more trouble
from importlib import import_module
import traceback


class PluginManager:


    class CommandContext:
        def __init__(self, parent, message_sender):
            self.chat = message_sender
            self.parent = parent
            self.config = parent.config["plugins"]

        def msg(self, message, target=None):
            prefix = ""
            if target:
                prefix = "/msg " + target + " "
            self.chat.put(('chat', prefix + message))


    def __init__(self, config, message_sender):
        self.config = config
        self.plugins = {}
        self.commands = {}
        self.transforms = {}
        self.msghandlers = []
        self.tick = []
        self.ctx = self.CommandContext(self, message_sender)

    def registerPlugin(self, plugin):
        self.plugins[plugin.name] = plugin
        for cmd in plugin.getCommands():
            names = getattr(cmd, "plushieCommand")
            for n in names:
                self.commands[n] = cmd
            # Add transforms
            self.transforms.update(getattr(cmd, "commandTransforms"))
        for tick in plugin.getTick():
            self.tick.append(tick)
        for handle in plugin.getMessageHandlers():
            self.msghandlers.append(handle)

    def registerPluginsFromList(self, pluginList, baseModule="plugins"):
        for plug in pluginList:
            self.registerPluginFromString(plug, baseModule)

    def registerPluginFromString(self, pluginName, baseModule="plugins"):
        # TODO: Check to make sure that there is a "." in the string
        path, className = pluginName.rsplit(".", 1)
        mod = import_module("{:s}.{:s}".format(baseModule, path))
        cls = getattr(mod, className)
        self.registerPlugin(cls())

    def signalCommand(self, message):
        if message.isCommand():
            args = message.msgArg()
            cmd = args[0][1:].lower()
            # Apply transforms
            if cmd in self.transforms:
                parts = self.transforms[cmd].split(" ")
                cmd = parts[0]
                # This is some nasty joojoo; the Message gets hot-modified here
                parts.extend(message.msgArg()[1:]) # For now only 1->many transforms are allowed
                message.msg = "!" + " ".join(parts)
            if cmd in self.commands:
                try:
                    self.commands[cmd](self.ctx, message)
                except:
                    # TODO: Get plugin from command name
                    print("[{:s}] Error:\n{:s}".format("Unknown Plugin", traceback.format_exc()))
                    # TODO: Disable plugin

    def signalTick(self):
        for cmd in self.tick:
            try:
                cmd(self.ctx)
            except:
                # TODO: Same stuff as in signalMessage()
                print("[{:s}] Error:\n{:s}".format("Unknown Plugin", traceback.format_exc()))

    def signalMessage(self, message):
        # Handle messages before passing to command handling
        for handler in self.msghandlers:
            try:
                handler(self.ctx, message)
            except:
                # TODO: See previous methods
                print("[{:s}] Error:\n{:s}".format("Unknown Plugin", traceback.format_exc()))

        if message.isCommand():
            self.signalCommand(message)

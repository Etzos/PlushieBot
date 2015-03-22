import fnmatch
import importlib
import os
import traceback

from plugins.plugin import PlushiePlugin


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
        """Officially registers a plugin instance with the plugin manager.

        Args:
            plugin (PlushiePlugin): Plugin instance to register.
        """
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

    def unregister_plugin(self, plugin):
        """Officially unregisters a plugin instance from the plugin manager."""
        for cmd in plugin.getCommands():
            for command_name in getattr(cmd, "plushieCommand"):
                del self.commands[command_name]
            for k, v in getattr(cmd, "commandTransforms"):
                del self.transforms[k]
        for tick in plugin.getTick():
            self.tick.remove(tick)
        for handle in plugin.getMessageHandlers():
            self.msghandlers.remove(handle)
        del self.plugins[plugin.name]

    def registerPluginsFromList(self, pluginList, baseModule="plugins"):
        """Registers a plugin given a list of plugins."""
        for plug in pluginList:
            self.registerPluginFromString(plug, baseModule)

    def registerPluginFromString(self, pluginName, baseModule="plugins"):
        """Registers a plugin given a string."""
        path, className = pluginName.rsplit(".", 1)
        mod = importlib.import_module("{:s}.{:s}".format(baseModule, path))
        cls = getattr(mod, className)
        self.registerPlugin(cls())

    def load_plugins(self, blacklist=[]):
        """Loads plugins from the :mod:`plugins` submodule automatically.

        Loads all plugins from the :mod:`plugins` submodule automatically while ignoring classes included in the
        blacklist arg.

        KWargs:
            blacklist (str[]): List of plugin classes to ignore.
        """
        # Search the plugins directory for names matching *?plugin.py (anything in front with at least one character)
        plugins = fnmatch.filter(os.listdir("./plugins"), "*?plugin.py")
        for plugin in map(lambda n: n.split(".")[0], plugins):
            if plugin in blacklist:
                continue
            # This is a bit hacky since I don't maintain a reference
            importlib.import_module("plugins.{!s}".format(plugin))
        # Now that all the relavant modules have been imported, grab the plugin classes
        for plugin_class in PlushiePlugin.__subclasses__():
            print(plugin_class)
            self.registerPlugin(plugin_class())

    def reload_plugin(self, plugin_name):
        """Reloads an existing plugin using the name of the plugin class."""
        try:
            plugin = self.plugins[plugin_name]
        except:
            return False
        class_name = plugin.__class__.__name__
        mod = importlib.import_module(plugin.__class__.__module__)
        self.unregister_plugin(plugin)
        newmod = importlib.reload(mod)
        cls = getattr(newmod, class_name)
        self.registerPlugin(cls())
        return True

    def signalCommand(self, message):
        if message.isCommand():
            args = message.msgArg()
            cmd = args[0][1:].lower()
            # Apply transforms
            if cmd in self.transforms:
                parts = self.transforms[cmd].split(" ")
                cmd = parts[0]
                # This is some nasty joojoo; the Message gets hot-modified here
                parts.extend(message.msgArg()[1:])  # For now only 1->many transforms are allowed
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

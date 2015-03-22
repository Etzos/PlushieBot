import fnmatch
import importlib
import os
import traceback

from plugins.plugin import PlushiePlugin


def plugin_error(command):
    """Prints an error message and traceback given the plugin method ``command``"""
    print("[{:s}] Error:\n{:s}".format(command.__self__.name, traceback.format_exc()))


class PluginManager:
    """Class specifically made for managing Plushie plugins."""

    class CommandContext:
        """Convience class of sorts that is passed into a plugin's method calls."""
        def __init__(self, parent, message_sender):
            self.chat = message_sender
            self.parent = parent
            self.config = parent.config["plugins"]

        def msg(self, message, target=None):
            """Sends a message to NEaB chat."""
            prefix = ""
            if target:
                prefix = "/msg " + target + " "
            self.chat.put(('chat', prefix + message))

    def __init__(self, config, message_sender):
        #: Stores the configuration file for Plushie.
        self.config = config
        #: Holds a dict of registered plugins in "Plugin Name":plugin_instance format.
        self.plugins = {}
        #: Holds a dict of commands in "!command":command_function format.
        self.commands = {}
        #: Holds a dict of transforms for commands.
        self.transforms = {}
        #: Holds a list of methods that are called for every message sent.
        self.msghandlers = []
        #: Holds a list of methods that are called for every tick (~4 seconds).
        self.tick = []
        #: The instance of the context class that gets passed into plugin methods.
        self.ctx = self.CommandContext(self, message_sender)

    def register_plugin(self, plugin):
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

    def register_from_list(self, plugin_list):
        """Registers a plugin given a list of plugins."""
        for plug in plugin_list:
            self.register_from_string(plug)

    def registerPluginFromString(self, plugin_name):
        """Registers a plugin given a string."""
        path, class_name = plugin_name.rsplit(".", 1)
        mod = importlib.import_module("{:s}.{:s}".format("plugins", path))
        cls = getattr(mod, class_name)
        self.register_plugin(cls())

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
            self.register_plugin(plugin_class())

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
        self.register_plugin(cls())
        return True

    def signalCommand(self, message):
        if message.isCommand():
            args = message.msgArg()
            cmd_name = args[0][1:].lower()
            # Apply transforms
            if cmd_name in self.transforms:
                parts = self.transforms[cmd_name].split(" ")
                cmd_name = parts[0]
                # This is some nasty joojoo; the Message gets hot-modified here
                parts.extend(message.msgArg()[1:])  # For now only 1->many transforms are allowed
                message.msg = "!" + " ".join(parts)
            if cmd_name in self.commands:
                cmd = self.commands[cmd_name]
                try:
                    cmd(self.ctx, message)
                except:
                    plugin_error(cmd)

    def signalTick(self):
        for cmd in self.tick:
            try:
                cmd(self.ctx)
            except:
                plugin_error(cmd)

    def signalMessage(self, message):
        # Handle messages before passing to command handling
        for handler in self.msghandlers:
            try:
                handler(self.ctx, message)
            except:
                plugin_error(handler)

        if message.isCommand():
            self.signalCommand(message)

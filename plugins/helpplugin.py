from .plugin import *


class HelpPlugin(PlushiePlugin):
    name = "PlushieBot Help Plugin"
    description = "Access documentation for PlushieBot commands"
    authors = ["Kitsune30", "Garth"]

    def __init__(self):
        self.documentation = None
        self.followingcmds = None
        self.cmd = None
        self.subcmd = None
        self.follows = None

# For all future command documentation:
# [] = optional command
# <> = required user input
# | = choice between items
    @plushieCmd("help")
    @commandDoc(extra="<command> [subcommand]",
                doc="Shows usage, documentation, and any subcommands of Plushie's commands")
    def retrieveDoc(self, ctx, msg):
        args = msg.getArgs()
        numargs = len(args)

        if numargs < 1:
            ctx.msg("Too few arguments. Please include a command and/or a subcommand.", msg.replyTo)
            return

        # Store a copy of the original args so that the *original* call can be printed
        original_args = args.copy()
        args = self.get_transformed(args[0], ctx)
        args.extend(original_args[1:])
        numargs = len(args)
        if numargs == 1:
            self.cmd = args[0].lower()
            self.subcmd = None
            self.follows = None
        elif numargs == 2:
            self.cmd = args[0].lower()
            self.subcmd = args[1]
            self.follows = None
        elif numargs > 2:
            self.cmd = args[0].lower()
            self.subcmd = args[-1:].lower()
            self.follows = args[-2:-1].lower()

        try:
            self.documentation = [(x['doc'], x['extra']) for x in ctx.parent.commands[self.cmd]._doc
                                  if x['follows'] == self.follows and (x['cmd'] == self.subcmd or
                                  self.subcmd in x['alias'])][0]
        except:
            ctx.msg("{:s} is not a command. Please use an existing command.".format(msg.noCmdMsg()), msg.replyTo)
            return
        should_follow = None if not self.subcmd else args[-1:]
        try:
            self.followingcmds = [x['cmd'] for x in ctx.parent.commands[self.cmd]._doc if
                                  x['follows'] == should_follow and x['cmd']]
        except:
            ctx.msg("[Plugin:Help] Error: Could not run the comprehension for following subcommands. Contact Garth or "
                    "WhiteKitsune.", msg.replyTo)
            return
        ctx.msg("Usage: !{:s}{:s} About: {:s}. Subcommands: {:s}"
                .format(" ".join(original_args[0:]),
                        " " + self.documentation[1] if self.documentation[1] else "",
                        self.documentation[0],
                        ", ".join(self.followingcmds) if len(self.followingcmds) > 0 else "None."),
                msg.replyTo)

    def get_transformed(self, command, ctx):
        """Returns the transformed version of the command and arguments as a list"""
        returns = [command]
        if command in ctx.parent.transforms:
            parts = ctx.parent.transforms[command].split(" ")
            returns = parts
        return returns

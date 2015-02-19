from .plugin import *

class HelpPlugin(PlushiePlugin):
    name = "PlushieBot Help Plugin"
    description = "Access documentation for PlushieBot commands"
    authors = ["WhiteKitsune"]
    
    def __init__(self):
        self.documentation = None
        self.followingcmds = None
        self.cmd = None
        self.subcmd = None
        self.follows = None
    
    @plushieCmd("help")
    def retrieveDoc(self, ctx, msg):
        args = msg.getArgs()
        numargs = len(args)
        
        if numargs < 1:
            ctx.msg("Too few arguments. Please include a command and/or a subcommand.", msg.replyTo)
            return
        elif numargs == 1:
            self.cmd = args[0]
            self.subcmd = None
            self.follows = None
        elif numargs == 2:
            self.cmd = args[0]
            self.subcmd = args[1]
            self.follows = None
        elif numargs > 2:
            self.cmd = args[0]
            self.subcmd = args[-1:]
            self.follows = args[-2:-1]
        
        try:
            self.documentation = [(x.doc, x.extra) for x in ctx.parent.commands[self.cmd]._doc if x.follows == self.follows and (x.cmd == self.subcmd or self.subcmd in x.alias)]
        except:
            ctx.msg("[Plugin:Help] Error: Could not run the comprehension to find documentations. Contact Garth or WhiteKitsune.", msg.replyTo)
            return
        try:
            self.followingcmds = [x.cmd for x in ctx.parent.commands[self.cmd]._doc if x.follows == self.follows]
        except:
            ctx.msg("[Plugin:Help] Error: Could not run the comprehension for following subcommands. Contact Garth or WhiteKitsune.", msg.replyTo)
            return
        ctx.msg("Results for \"help {:s}\": {:s}. Subcommands: {:s}".format(args[0:], self.documentation[0], self.follwingcmds[0]), msg.replyTo)
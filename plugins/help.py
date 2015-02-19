from .plugin import *

class HelpPlugin
    name = "PlushieBot Help Plugin"
    description = "Access documentation for PlushieBot commands"
    authors = ["WhiteKitsune"]
    
    def __init__(self):
    self.documentation = None
    self.cmd = None
    self.subcmd = None
    self.follows = None
    
    @plushieCmd("help")
    def retrieveDoc(self, ctx, msg)
        args = msg.getsArgs()
        
        if len(args) < 1:
            ctx.msg("Too few arguments. Please include a command and/or a subcommand.", msg.replyTo)
            return
        elif len(args) == 1:
            self.cmd = args[0]
            self.subcmd = None
            self.follows = None
        elif len(args) == 2:
            self.cmd = args[0]
            self.subcmd = args[1]
            self.follows = None
        elif leng(args) > 2:
            self.cmd = args[0]
            self.subcmd = [-1:]
            self.follows = [-2:-1]
        
        try:
            self.documentation = [(x.doc, x.extra) for x in ctx.parent.command[self.cmd]._doc if x.follows == self.follows and (x.cmd == self.subcmd or self.subcmd in x.alias)]
        except:
            ctx.msg("[Plugin:Help] Error: Could not run the comprehension to find documentations. Contact Garth or WhiteKitsune.", msg.replyTo)
            return
        try:
            self.followingcmds = [x.cmd for x in ctx.parent.commands[self.cmd]._doc if x.follows == self.follows]
        except:
            ctx.msg("[Plugin:Help] Error: Could not run the comprehension for following subcommands. Contact Garth or WhiteKitsune.", msg.replyTo)
            return
        ctx.msg("Results for /"help {:s}/": {:s}. Subcommands: {:s}".format(args[0:], self.documentation, self.follwingcmds), msg.replyTo)
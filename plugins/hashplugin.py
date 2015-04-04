from .plugin import PlushiePlugin, plushieCmd, commandDoc

import hashlib


class HashPlugin(PlushiePlugin):
    name = "Hashing Plugin"
    description = "Turn a string into it's hashed value. (Supports SHA1 and MD5)"
    authors = ["Garth"]

    @plushieCmd("hash")
    @commandDoc(doc="Returns a hash")
    @commandDoc(cmd="md5", extra="<string to hash>", doc="Returns a md5 sum of <string to hash>")
    @commandDoc(cmd="sah1", extra="<string to hash>", doc="Returns a sha1 sum of <string to hash>")
    def run(self, ctx, msg):
        args = msg.getArgs()
        argLen = len(args)
        if argLen < 1:
            ctx.msg("I need to know the hashing method you want to use.", msg.replyTo)
            return
        elif argLen < 2:
            ctx.msg("I need to have something to hash.", msg.replyTo)
            return

        hashtype = args[0].lower()
        remains = " ".join(args[1:])

        if hashtype == "md5":
            ctx.msg("MD5 sum: " + hashlib.md5(bytes(remains, 'ascii')).hexdigest(), msg.replyTo)
        elif hashtype == "sha1":
            ctx.msg("SHA1 sum: " + hashlib.sha1(bytes(remains, 'ascii')).hexdigest(), msg.replyTo)
        else:
            ctx.msg("I'm sorry, I don't know the hashing algorithm '" + hashtype + "'", msg.replyTo)

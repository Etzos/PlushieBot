from .plugin import *

import urllib.parse

class GooglePlugin(PlushiePlugin):
    name = "Google Plugin"
    description = "Have Plushie search Google for you"
    authors = ["Kitsune30"]
    #Shamelessly stolen code from: Garth

    @plushieCmd("google")
    def googleStuff(self, ctx, msg):
        args = msg.getArgs()

        if len(args) < 1:
            ctx.msg("I can't google nothing.", msg.replyTo)
            return

        if len(args) > 0:
            url = urllib.parse.quote_plus(msg.noCmdMsg())
            ctx.msg("Here you go: https://www.google.com/#q={:s}".format(url), msg.replyTo)
        else:
            ctx.msg("Something has failed. Please contact Garth about it.", msg.replyTo)

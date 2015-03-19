from .plugin import *
from amarok import MprisPlaying


class ListenPlugin(PlushiePlugin):
    name = "Now Playing Plugin"
    description = "Display what Amarok is playing with a command"
    authors = ["Garth"]

    @plushieCmd("listen", "playing")
    @commandDoc(doc="Returns what is playing on Plushie's server's computer")
    def listen(self, ctx, msg):
        amarok = MprisPlaying()
        amarok.getData("org.mpris.MediaPlayer2.amarok",
                       "/org/mpris/MediaPlayer2")
        spotify = MprisPlaying()
        spotify.getData("org.mpris.MediaPlayer2.spotify",
                        "/org/mpris/MediaPlayer2")

        baseMsg = "Garth is listening to '{:s}' ({:s}) by '{:s}' on '{:s}' using {:s}. "
        reply = ""

        if amarok.getTitle():
            reply += baseMsg.format(amarok.getTitle(), amarok.getStatus(), amarok.getArtist(), amarok.getAlbum(),
                                    "Amarok")
        if spotify.getTitle():
            reply += baseMsg.format(spotify.getTitle(), spotify.getStatus(), spotify.getArtist(), spotify.getAlbum(),
                                    "Spotify")

        if reply == "":
            ctx.msg("Garth is not listening to any music right now",
                    msg.replyTo)
        else:
            ctx.msg(reply, msg.replyTo)

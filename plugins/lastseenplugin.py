from .plugin import *

import sqlite3
import datetime


class LastSeenPlugin(PlushiePlugin):
    name = "Last Said Plugin"
    description = "See the last thing someone said"
    authors = ["Garth"]

    def __init__(self):
        self.db = sqlite3.connect("chat.db", detect_types=sqlite3.PARSE_COLNAMES)

    @plushieCmd("lastsaid")
    @commandDoc(extra="<player> [<number>]",
                doc="Returns <player>'s message from <number> messages ago. Without <number>, defaults to last "
                "message they have said")
    def run(self, ctx, msg):
        args = msg.getArgs()
        argsLen = len(args)

        if argsLen < 1:
            ctx.msg("I do not know who you are talking about {:s}.".format(msg.player), msg.replyTo)
            return

        target = args[0].lower()
        howMany = 1
        if argsLen > 1:
            try:
                howMany = int(args[1])
            except ValueError:
                ctx.msg("You have to put nothing or a number after a player's name.", msg.replyTo)
                return
            if howMany < 1:
                ctx.msg("You have to provide a positive number.", msg.replyTo)
                return
            elif howMany > 30:
                ctx.msg("I'm sorry, but I don't remember that far back.", msg.replyTo)
                return

        # If the target is the player who's asking, add one to make sure that
        # the current !lastsaid isn't printed
        if target == msg.player.lower():
            howMany += 1

        if target == "plushie":
            ctx.msg("I'm not going to quote myself.", msg.replyTo)
            return

        said = self.getLastMessage(target, howMany)
        if not said:
            ctx.msg("I haven't seen {:s} say anything{:s}.".format(args[0], "" if howMany < 2 else " that far back"),
                    msg.replyTo)
            return

        saiddate = said[4]
        curdate = datetime.datetime.now(datetime.timezone.utc)
        dtformat = "%H:%M:%S UTC"
        if curdate.year != saiddate.year:
            dtformat = "%Y-%m-%d " + dtformat
        elif curdate.month != saiddate.month or curdate.day != saiddate.day:
            dtformat = "%m-%d " + dtformat

        time = said[4].strftime(dtformat)
        ctx.msg("[{:s}] {:s}> {:s}".format(time, said[1], said[3]), msg.replyTo)

    def getLastMessage(self, player, howMany=1):
        # Make this select the right one
        howMany -= 1
        res = self.db.execute("""
            SELECT id, speaker, whisper, message, time as "ts [timestamp]" FROM history
            WHERE lower(speaker) = ? AND whisper > 0
            ORDER BY time DESC LIMIT 1 OFFSET ?
            """, (player.lower(), howMany))
        # WHERE lower(speaker) = ? AND whisper > 0 AND time < datetime('now', '-2 seconds')
        row = res.fetchone()
        if not row:
            return None
        return row

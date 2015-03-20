from .plugin import PlushiePlugin, plushieCmd, commandDoc

import sqlite3


class StatPlugin(PlushiePlugin):
    name = "PlushieBot Statistics Plugin"
    description = "Access to various stats from PlushieBot"
    authors = ["Garth"]

    def __init__(self):
        self.db = sqlite3.connect("chat.db")

    @plushieCmd("stats", "stat", transforms={"toplines": "stats toplines"})
    @commandDoc(doc="Has Plushie return various stats about chat lines")
    @commandDoc(cmd="lines", extra="<player>", doc="Returns how many lines Plushie has seen <player> say")
    @commandDoc(cmd="toplines",
                doc="Returns the top 5 players who have spoken the most and the amount of lines they have said")
    @commandDoc(cmd="totallines", doc="Returns how many lines Plushie has seen in total")
    @commandDoc(cmd="linerank", extra="[player]", doc="Returns the rank and how many lines you or (player) has said")
    @commandDoc(cmd="rank", extra="<number>",
                doc="Returns the player and the amount of lines they have said at rank <number>")
    def delegate(self, ctx, msg):
        args = msg.getArgs()
        arglen = len(args)

        if arglen < 1:
            ctx.msg("You must provide at least one argument", msg.replyTo)
            return

        if args[0].lower() == "lines":
            if arglen < 2:
                ctx.msg("You must supply at least two arguments for this function.", msg.replyTo)
                return
            amount = self.getNumLines2(args[1])
            if amount == 0:
                reply = "I haven't seen {:s} say anything.".format(args[1])
            else:
                reply = "I have seen {:s} say {:d} line{:s} in chat.".format(args[1], amount,
                                                                             "" if amount == 1 else "s")
            ctx.msg(reply, msg.replyTo)
        elif args[0].lower() == "toplines":
            lines = self.getTopLines()
            mostStat = ", ".join("{:s} [{:d}]".format(a[0], a[1]) for a in lines)
            ctx.msg("The players who speak the most are: {:s}".format(mostStat), msg.replyTo)
        elif args[0].lower() == "totallines":
            query = self.db.execute("SELECT SUM(lines) FROM speakers")
            res = query.fetchone()
            if not res:
                amt = 0
            else:
                amt = res[0]
            ctx.msg("I have seen a total of {:d} lines said.".format(amt), msg.replyTo)
        elif args[0].lower() == "linerank":
            rankToGet = msg.player
            # If the player enters another argument, assume it's a player name
            if arglen > 1:
                rankToGet = args[1]
            rank = self.getLineRank(rankToGet)
            if not rank:
                ctx.msg("I haven't seen {:s} say anything.".format(rankToGet), msg.replyTo)
                return
            ctx.msg("{:s} the #{:d} most talkative player with {:d} lines."
                    .format("You are" if rankToGet == msg.player else "{:s} is".format(rankToGet), rank[0], rank[1]),
                    msg.replyTo)
        elif args[0].lower() == "rank":
            if arglen < 2:
                ctx.msg("You must supply a number to the rank subcommand.", msg.replyTo)
                return
            try:
                toGet = int(args[1])
            except ValueError:
                ctx.msg("Unknown rank number '{:s}'.".format(args[1]), msg.replyTo)
                return
            if toGet < 1:
                ctx.msg("You must supply number greater than zero.", msg.replyTo)
                return
            rank = self.getPlayerAtRank(toGet)
            if not rank:
                ctx.msg("I don't know anyone at rank #{:d}.".format(toGet), msg.replyTo)
                return
            ctx.msg("The player at rank #{:d} for the most chat lines is {:s} [{:d}].".format(toGet, rank[0], rank[1]),
                    msg.replyTo)
        else:
            ctx.msg("Sorry, I don't recognize the '{:s}' sub-command.".format(args[0]), msg.replyTo)

    def getNumLines(self, player):
        res = self.db.execute("""
            SELECT COUNT(*) FROM history
            WHERE lower(speaker) = ? AND whisper > 0
            """, (player.lower(),))
        rows = res.fetchone()
        return rows[0]

    def getNumLines2(self, player):
        res = self.db.execute("""
            SELECT lines FROM speakers WHERE lower(speaker) = ?
            """, (player.lower(),))
        rows = res.fetchone()
        return 0 if not rows else rows[0]

    def getTopLines(self):
        res = self.db.execute("""
            SELECT speaker, lines FROM speakers
            ORDER BY lines DESC
            LIMIT 5
            """)
        rows = res.fetchall()
        if not rows:
            return None
        else:
            return rows

    def getLineRank(self, player):
        res = self.db.execute("""
            SELECT COUNT(*) AS above,
                   (SELECT lines FROM speakers WHERE LOWER(speaker) = ?) AS amount
            FROM speakers
            WHERE lines > amount
            """, (player.lower(),))
        rows = res.fetchone()
        if not rows:
            return None
        elif not rows[1]:
            return None
        else:
            return (rows[0]+1, rows[1])  # Add 1 because rank is number of people above plus one (yourself)

    def getPlayerAtRank(self, rank):
        res = self.db.execute("""
            SELECT speaker, lines FROM speakers
            ORDER BY lines DESC
            LIMIT 1 OFFSET ?
            """, (rank-1,))
        row = res.fetchone()
        if not row:
            return None
        elif not row[1]:
            return None
        else:
            return (row[0], row[1])

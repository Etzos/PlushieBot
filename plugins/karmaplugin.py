from .plugin import *

import sqlite3


class KarmaPlugin(PlushiePlugin):
    name = "Karma Management Plugin"
    description = "Give players (and other arbitrary items) karma"
    authors = ["Garth"]

    def __init__(self):
        self.db = sqlite3.connect("karma.db")

        self.db.execute("""
            CREATE TABLE IF NOT EXISTS karma (
            id INTEGER PRIMARY KEY,
            item TEXT,
            itemNormalized TEXT UNIQUE ON CONFLICT IGNORE,
            added INTEGER,
            subtracted INTEGER
            )""")
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            player TEXT,
            target TEXT,
            change INTEGER,
            changetime TEXT
            )""")
        # TODO: Delete old history entries (older than say a day)
        self.db.execute("""
            CREATE TABLE IF NOT EXISTS timeout (
            id INTEGER PRIMARY KEY,
            player TEXT UNIQUE ON CONFLICT IGNORE,
            dateadded TEXT
            )""")
        self.db.commit()

    @plushieCmd("karma", "aura")
    @commandDoc(doc="Control or view karma")
    @commandDoc(cmd="increase", doc="View items with the most increases")
    @commandDoc(cmd="decrease", doc="View items with the most decreases")
    @commandDoc(cmd="most", doc="View items with the most changes")
    @commandDoc(cmd="++", alias=("add",), extra="<item name>", doc="Increase the karma of <item name> by 1")
    @commandDoc(cmd="--", alias=("sub",), extra="<item name>", doc="Decrease the karma of <item name> by 1")
    @commandDoc(cmd="status", extra="[<item name>]", doc="Gets either <item name>'s karma or your karma")
    def run(self, ctx, msg):
        bodyParts = msg.getArgs()
        num = len(bodyParts)
        player = msg.player
        name = msg.getCmd()

        if num < 1:
            ctx.msg("{:s}: Your {:s} is {:d}.".format(player, name, self.getKarma(player)), msg.replyTo)
        elif num == 1:
            if bodyParts[0] == "increase":
                postStr = "The items with the most increases are: "
                for r in self.most("increase", 5):
                    postStr += "{:s}: ({:d}) [+{:d} / -{:d}], ".format(r[0], r[3], r[1], r[2])
                ctx.msg(postStr, msg.replyTo)
            elif bodyParts[0] == "decrease":
                postStr = "The items with the most decreases are: "
                for r in self.most("decrease", 5):
                    postStr += "{:s}: ({:d}) [+{:d} / -{:d}], ".format(r[0], r[3], r[1], r[2])
                ctx.msg(postStr, msg.replyTo)
            elif bodyParts[0] == "most":
                postStr = "The items with the most {:s} are: ".format(name)
                for r in self.most("most", 5):
                    postStr += "{:s}: ({:d}) [+{:d} / -{:d}], ".format(r[0], r[3], r[1], r[2])
                ctx.msg(postStr, msg.replyTo)
            else:
                ctx.msg("{:s}: Your {:s} is {:d}.".format(player, name, self.getKarma(player)), msg.replyTo)
        elif bodyParts[0] == "++" or bodyParts[0] == "add":
            if msg.isWhisper:
                ctx.msg("Privately changing {:s} isn't allowed.".format(name), player)
                return
            elif player == bodyParts[1]:
                ctx.msg("You cannot change your own {:s}.".format(name), player)
                return
            if (not self.checkTimeout(player)) or (not self.checkHistory(player)):
                ctx.msg("You have made too many {:s} changes recently and " +
                        "have been placed on timeout.".format(name), player)
                return
            self.addHistory(player, bodyParts[1], True)
            self.addKarma(bodyParts[1])
            ctx.msg("{:s}'s {:s} increased.".format(bodyParts[1], name), player)
        elif bodyParts[0] == "--" or bodyParts[0] == "sub":
            if msg.isWhisper:
                ctx.msg("Privately changing {:s} isn't allowed.".format(name), player)
                return
            elif player == bodyParts[1]:
                ctx.msg("You cannot change your own {:s}.".format(name), player)
                return
            if (not self.checkTimeout(player)) or (not self.checkHistory(player)):
                ctx.msg("You have made too many {:s} changes recently and " +
                        "have been placed on timeout.".format(name), player)
                return
            self.addHistory(player, bodyParts[1], False)
            self.subKarma(bodyParts[1])
            ctx.msg("{:s}'s {:s} decreased.".format(bodyParts[1], name), player)
        elif bodyParts[0] == "status":
            ctx.msg("'{:s}' has {:d} {:s}.".format(bodyParts[1], self.getKarma(bodyParts[1]), name),
                    msg.replyTo)

    def getKarma(self, item):
        res = self.db.execute("""SELECT added, subtracted
                                 FROM karma
                                 WHERE itemNormalized=?""",
                              (item.lower(),))
        row = res.fetchone()
        if not row:
            return 0
        else:
            return row[0] - row[1]

    def addKarma(self, item):
        item = item[:20]
        norm = item.lower()
        self.db.execute("""INSERT INTO karma VALUES (NULL, ?, ?, 0, 0)""",
                        (item, norm,))
        self.db.execute("""UPDATE karma
                           SET added=added+1
                           WHERE itemNormalized = ?""",
                        (norm,))
        self.db.commit()

    def subKarma(self, item):
        item = item[:20]
        norm = item.lower()
        self.db.execute("""INSERT INTO karma VALUES (NULL, ?, ?, 0, 0)""",
                        (item, norm,))
        self.db.execute("""UPDATE karma
                           SET subtracted=subtracted+1
                           WHERE itemNormalized = ?""",
                        (norm,))
        self.db.commit()

    def most(self, order="increase", limit=5):
        if order == "increase":
            orderby = "added"
        elif order == "decrease":
            orderby = "subtracted"
        else:
            orderby = "added-subtracted"
        res = self.db.execute("""SELECT item, added, subtracted,
                                        added-subtracted
                                 FROM karma
                                 ORDER BY ? DESC
                                 LIMIT ?""", (orderby, limit,))
        return res.fetchall()

    def addHistory(self, player, target, add=True):
        self.db.execute("""
            INSERT INTO history (id, player, target, change, changetime)
            VALUES (NULL, ?, ?, ?, datetime('now'))
            """, (player, target, 1 if add is True else -1,))
        self.db.commit()

    def checkHistory(self, player):
        res = self.db.execute("""
            SELECT COUNT(*) FROM history
            WHERE player = ?
            AND datetime(changetime) >= datetime('now', '-30 minutes')
            """, (player,))
        rows = res.fetchone()
        print("Length: ", rows[0])
        if rows[0] >= 10:
            self.addTimeout(player)
            return False
        return True

    def addTimeout(self, player):
        self.db.execute("""
            INSERT INTO timeout
            VALUES (NULL, ?, datetime('now'))
            """, (player,))
        self.db.execute("""
            UPDATE timeout
            SET dateadded = datetime('now')
            WHERE player = ?
            """, (player,))
        self.db.commit()

    def checkTimeout(self, player):
        res = self.db.execute("""
            SELECT * FROM timeout
            WHERE player = ?
            AND datetime(dateadded) >= datetime('now', '-60 minutes')
            """, (player,))
        rows = res.fetchall()
        if not rows:
            return True
        return False

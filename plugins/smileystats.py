from .plugin import *
from message import smileyNums

import sqlite3
import os.path


class SmileyStatsPlugin(PlushiePlugin):
    name = "Smiley Statistics"
    description = "Saves info on the number of smilies players have used and give access to these stats"
    authors = ["Garth"]
    
    def __init__(self):
        dbfile = "smileycounter.db"
        firstStart = not os.path.isfile(dbfile)
        self.db = sqlite3.connect(dbfile)
        if firstStart:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS Smilies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, -- NOTE: This is NOT the NEaB ID, but a personal ID
                    smiley TEXT NOT NULL UNIQUE
                )""")
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS SmileyCount (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    speaker TEXT NOT NULL,
                    smiley INTEGER NOT NULL,
                    count INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY(smiley) REFERENCES Smilies(id),
                    UNIQUE (speaker, smiley) ON CONFLICT IGNORE
                )""")
            self.db.executemany("INSERT INTO Smilies (smiley) VALUES (?)", ((s,) for s in smileyNums.values()))
            self.db.commit()

    @plushieCmd("smileycount")
    def smileyCount(self, ctx, msg):
        bodyParts = msg.getArgs()
        num = len(bodyParts)
        player = msg.player

        if num < 1:
            speaker = player
            smiley = ":)"
        elif num == 1:
            speaker = player
            smiley = bodyParts[0]
        else:
            speaker = bodyParts[1]
            smiley = bodyParts[0]
        smileyID = self.getSmileyId(smiley)
        
        if not smileyID:
            ctx.msg("%s is not a known smiley." % (smiley,), msg.replyTo)
            return
        #print("Get: %d" % (smileyID,))
        query = self.db.execute("SELECT count FROM SmileyCount WHERE speaker = ? AND smiley = ?", (speaker.lower(), smileyID))
        res = query.fetchone()
        if not res:
            amt = 0
        else:
            amt = res[0]

        ctx.msg("I have seen %s use the %s smiley %d times." % (speaker, smiley, amt), msg.replyTo)

    @plushieMsg()
    def storeData(self, ctx, msg):
        if not msg.msg or msg.player.lower() == "plushie" or msg.whisper < 1:
            return
        if msg.getCmd() == "smileycount":
            return
        # Find any smiley's in the message
        # If there is one, add the player, smiley
        playerNorm = msg.player.lower()
        sm = self.getSmilies(msg.msg)
        for smiley, amt in sm.items():
            # Get Smiley ID, insert (player, smiley) combo, update number
            smileyID = self.getSmileyId(smiley, True)
            if not smileyID:
                return
            #print("Set: %d" % (smileyID,))
            # Force the (player, smiley) tuple to exist
            self.db.execute("INSERT INTO SmileyCount (speaker, smiley) VALUES (?, ?)", (playerNorm, smileyID))
            # Update existing value
            q = self.db.execute("UPDATE SmileyCount SET count=count+? WHERE speaker = ? AND smiley = ?", (amt, playerNorm, smileyID))
            self.db.commit()

    def getSmileyId(self, smiley, insertNew=False):
        query = self.db.execute("SELECT id FROM Smilies WHERE smiley = ?", (smiley,))
        res = query.fetchone()
        if res is None:
            print("Unknown smiley '%s'" % smiley)
            # TODO: Insert new smiley into Smilies and return new ID (if insertNew == True)
            return None
        return res[0]

    def getSmilies(self, text):
        res = dict()
        for smiley in smileyNums.values():
            amt = text.count(smiley)
            if amt > 0:
                res[smiley] = text.count(smiley)
        return res
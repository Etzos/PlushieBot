import json
from multiprocessing import Process, Pipe
import socket
import sqlite3
from threading import Thread
import urllib.error

#from loop.lib import Profile, ChatLib, ChatOnline
from lib import Profile, ChatLib, ChatOnline
from message import Message
from pluginmanager import PluginManager


def loadConfig(name="config.json"):
    config_file = open(name, "r")
    return json.loads(config_file.read())

def botRunner(p):
    config = loadConfig()
    botProfile = Profile(config["username"])
    isAuth = botProfile.auth(config["password"])
    if not isAuth:
        print("Unable to auth properly.")
        # TODO: Send a message using p to tell main process that we're dying
        return

    c = ChatLib(botProfile)
    o = ChatOnline(botProfile)
    pluginList = [
            "celebrateplugin.CelebratePlugin",
            "choiceplugin.ChoicePlugin",
            "googleplugin.GooglePlugin",
            "grabplugin.GrabPlugin",
            "greetplugin.GreetPlugin",
            "hangmanplugin.HangmanPlugin",
            "hashplugin.HashPlugin",
            "hugplugin.HugPlugin",
            "karmaplugin.KarmaPlugin",
            "kickplugin.KickPlugin",
            "lastseenplugin.LastSeenPlugin",
            "listplugin.ListPlugin",
#            "listenplugin.ListenPlugin",
            "mathplugin.MathPlugin",
            "mumbleplugin.MumblePlugin",
            "pingplugin.PingPlugin",
            "rpsplugin.RPSPlugin",
            "sayplugin.SayPlugin",
            "smileystats.SmileyStatsPlugin",
            "stabplugin.StabPlugin",
            "statplugin.StatPlugin",
            "sysplugin.SysPlugin",
            "timeplugin.TimePlugin",
            "tmpplugin.TmpPlugin",
            "werewolfplugin.WerewolfPlugin",
            "wikiplugin.WikiPlugin"
        ]
    pm = PluginManager(c, config)
    pm.registerPluginsFromList(pluginList)

    onlineCounter = 0
    msgList = []

    try:
        # Bring the last message up to date
        throwaway = c.getRawMessages()
        # Put self in online list
        o.poll(0)
    except:
        print("Error attempting to start: Unable to do first poll. Process dying.")
        return

    db = sqlite3.connect("chat.db")
    db.execute("""
        CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        speaker TEXT NOT NULL,
        whisper INTEGER NOT NULL, -- -1 = whisper from plushie, 0 = whisper to plushie, 1 = normal message
        message TEXT NOT NULL,
        time TEXT NOT NULL
        )""")
    db.execute("""
        CREATE TABLE IF NOT EXISTS flood (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        player TEXT NOT NULL,
        threatIndex INTEGER NOT NULL,
        time TEXT NOT NULL
        )""")
    db.execute("""
        CREATE VIEW IF NOT EXISTS "speakers" AS
            SELECT speaker, COUNT(LOWER(speaker))
            AS lines FROM history WHERE whisper = 1
            GROUP BY LOWER(speaker)
        """)
    db.commit()

    while True:
        # NOTE: The p.poll() call is what blocks this process for the 4 seconds between online checks
        stop = False
        if p.poll(4):
            print("Getting something")
            res = p.recv()
            print(res)
            if res == "stop":
                stop = True

        if stop:
            break

        # Run chat input checker
        if onlineCounter > 2:
            try:
                o.poll(0)
                onlineCounter = 0;
            except urllib.error.HTTPError:
                onlineCounter = 10
                pass
            except urllib.error.URLError:
                onlineCounter = 10
                pass
        else:
            onlineCounter += 1

        try:
            msgs = c.getRawMessageList()
            # TODO: Insert them in order (that probably means prepending them so use a deque)
            msgList.extend(msgs)
        except urllib.error.HTTPError:
            print("HTTPError Encountered")
            pass
        except urllib.error.URLError:
            print("URLError Encountered")
            pass
        except socket.gaierror:
            print("Teh Internetz r collapsin!")
            pass

        # Ticks run *after* checking online list to make sure Plushie doesn't overrun time
        pm.signalTick()

        # Check every message that came in
        for msg in msgList:
            if not msg:
                continue

            msgObj = Message(msg)

            if not msgObj.type:
                print("%s" % (msgObj.raw,))
            else:
                print("player: %s, (%s) message: %s" % (msgObj.player, msgObj.whisper, msgObj.msg))
            print("")
            # Store message in db (but only if it's actually a message)
            if msgObj.type:
                db.execute("""
                    INSERT INTO history
                    (speaker, whisper, message, time)
                    VALUES
                    (?, ?, ?, datetime('now'))
                    """, (msgObj.player, msgObj.whisper, msgObj.msg))
                db.commit()
            pm.signalMessage(msgObj)

        # All messages have been processed, so empty the list
        del msgList[:]


if __name__ == '__main__':
    # Use a Process to make sure that it checks every 4 seconds (instead of being blocked by the GIL)
    parentPipe, childPipe = Pipe()
#    runnerEnd, managerEnd = Pipe()
    sched = Process(target=botRunner, args=(childPipe,))
    #runner = Process(target=botRunner, args=(runnerEnd,))
    sched.start()
    while True:
        r = input("> ")
        if r == "exit" or r == "stop":
            print("Stopping PlushieBot...")
            parentPipe.send("stop")
            sched.join()
            break
        print(r)

    sched.join()
    print("Stopped")

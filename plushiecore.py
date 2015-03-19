import sqlite3
import time
import queue

from message import Message
from pluginmanager import PluginManager


def run_plushie(config, outputs, inputs):
    pluginList = [
            "celebrateplugin.CelebratePlugin",
            "choiceplugin.ChoicePlugin",
            "grabplugin.GrabPlugin",
            "greetplugin.GreetPlugin",
            "hangmanplugin.HangmanPlugin",
            "hashplugin.HashPlugin",
            "helpplugin.HelpPlugin",
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
            "searchplugin.SearchPlugin",
            "smileystats.SmileyStatsPlugin",
            "stabplugin.StabPlugin",
            "statplugin.StatPlugin",
            "sysplugin.SysPlugin",
            "timeplugin.TimePlugin",
            "tmpplugin.TmpPlugin",
            "werewolfplugin.WerewolfPlugin",
        ]

    # TODO: Make PluginManager use a different approach for sending messages
    pm = PluginManager(config, outputs)
    pm.registerPluginsFromList(pluginList)

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

    current_time = time.time()
    previous_time = current_time
    tick_time = 4 # seconds between 'ticks'
    while True:
        current_time = time.time()
        timediff = current_time - previous_time

        if timediff >= tick_time:
            previous_time = current_time
            pm.signalTick()

        try:
            # Wait for a message for tick_time - time elapsed (which *should* always be positive, but just in case
            # clamp to 0)
            message = inputs.get(True, max(tick_time - timediff, 0))
        except queue.Empty:
            # If the queue is empty, that means it's time to recalcualte the timediff so loop again
            continue

        if message[0] == "system":
            if message[1] == "stop":
                break
            else:
                print("Unknown message: " + message[1])
                continue

        chat_message = Message(message[1])

        # If the message is an actual message and not an action/system message
        if chat_message.type:
            print("Player: {:s}, ({:d}) Message: {:s}".format(chat_message.player,
                                                              chat_message.whisper,
                                                              chat_message.msg))
            # Store the line in the chat history
            db.execute("""
                INSERT INTO history
                (speaker, whisper, message, time)
                VALUES
                (?, ?, ?, datetime('now'))
                """, (chat_message.player,
                      chat_message.whisper,
                      chat_message.msg))
            db.commit()
            pm.signalMessage(chat_message)
        else:
            print(chat_message.raw)

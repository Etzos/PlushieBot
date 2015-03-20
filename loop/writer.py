#!/usr/bin/env python3
from time import strftime


def construct_message(sender, message, whisper=False, time="00:00"):
    """External API-like method for simulating sending a message"""
    constructed_message = "{:s} {:s}&gt; {:s}".format(
        time,
        "{:s}{:s}".format("from " if whisper else "", sender),
        message
    )
    return constructed_message


def full_message(sender, message, whisper=False):
    """Another external API, useful for easily creating a message"""
    time = strftime("%H:%M")
    return construct_message(sender, message, whisper, time)


def read_log(logfile, destructive=False):
    """Reads a log file

    This is an external API
    """
    messages = []
    with open(logfile, "a+") as f:
        f.seek(0)
        for line in f:
            stripped = line.rstrip('\n')
            if stripped == "":
                continue
            messages.append(line)
    if destructive:
        open(logfile, "w").close()
    return messages


def write_log(logfile, backlog):
    """Writest to a log file

    This is an external API
    """
    with open(logfile, "a+") as f:
        for line in backlog:
            f.write("{:s}\n".format(line))


# Everything below is no longer used externally
def get_username(player_namer):
    t = input("(Player Name)> ")
    if t != "":
        return t
    return player_name


def get_time(time):
    t = input("(Time)> ")
    if t != "":
        return t
    return time


def get_msgs(backlog, time, player_name, whisper_mode=False):
    print("Enter messages. Use '!!' to stop.".format("whispers" if whisper_mode else "messages"))
    prompt = "({:s}: {:s}@{:s})> ".format("Whisper" if whisper_mode else "Message",
                                          player_name,
                                          time)
    while True:
        line = input(prompt)
        if line == "!!":
            break
        backlog.append(construct_message(player_name, line, whisper_mode, time))
    return backlog


def main_prompt():
    player_name = "Guest"
    time = "00:00"
    backlog = []
    print("Started...")
    while True:
        line = input("> ")
        if line == "name":
            player_name = get_username(player_name)
        elif line == "time":
            time = get_time(time)
        elif line == "msg":
            backlog = get_msgs(backlog, time, player_name)
        elif line == "whisper":
            backlog = get_msgs(backlog, time, player_name, True)
        elif line == "flush":
            write_log("input.log", backlog)
            del backlog[:]
        elif line == "exit":
            break
        else:
            print("Unrecognized command '{:s}'".format(line))

if __name__ == "__main__":
    main_prompt()

import re

msgReg = re.compile('(?:\d+\:\d+) (?P<whisper>to|from)? ?' +
                    '(?P<player>[\w\-\.\ ]+[\w\-\.])(?:(?: &gt;)|(?:&gt;)) ' +
                    '(?P<message>.+)')
tagStrip = re.compile('<[^<]+?>')
linkRepl = re.compile('<a href=(.+?) (?:.*?)>(?:.*?)</a>', re.IGNORECASE)
entityRepl = re.compile('&(gt|lt|amp|trade);')
smileyRepl = re.compile('<img src=smilies/(\d+).gif align=center>')
smileyNums = {
    "0": ":)", "1": ":P", "2": ":O", "3": ":(", "4": ":-/", "5": ";)",
    "6": ":D", "7": "8)", "8": "B)", "9": "XD", "10": "T.T", "11": "^^'",
    "12": "^.^", "13": "O.O", "14": "8|", "15": "\M/", "16": ">.<", "17": "XP",
    "18": "o.O", "19": "-.-", "20": "(:<", "21": "f/", "22": ":S", "23": "*.*",
    "24": ":X", "25": "X.X", "26": "$.$", "27": "o@@o", "28": "9.9", "29": "O:<",
    "30": "B|", "31": "B(", "32": "B0", "33": "@.@", "34": "^**^", "35": "9.6",
    "36": "/.O", "37": "d.b", "38": ">.>", "39": "=^_^="
}


def linkReplaceFunc(m):
    link = m.group(1)
    return link


def htmlEntityReplaceFunc(m):
    part = m.group(1)
    if part == "gt":
        return ">"
    elif part == "lt":
        return "<"
    elif part == "amp":
        return "&"
    elif part == "trade":
        return ""
    else:
        return part


def smileyReplaceFunc(m):
    num = m.group(1)
    if num in smileyNums:
        return smileyNums[num]
    else:
        print(num)
    return ""


class Message:

    def __init__(self, msg):
        # TODO: Handle messages other than normal messsages (i.e. /me commands)
        self.raw = msg
        self.player = None
        self.msg = None
        self.whisper = 1  # 1 = normal message, 0 = whisper from player, -1 = whisper from me
        self.isWhisper = False  # This is True if a whisper from someone false in all other cases
        self.replyTo = None
        self.type = None
        self.time = None

        # Replace smilies
        msg = smileyRepl.sub(smileyReplaceFunc, msg)
        # Replace links
        msg = linkRepl.sub(linkReplaceFunc, msg)

        # Remove HTML tags from the message
        tagless = tagStrip.sub("", msg)
        # TODO: This is basically a full clean message here
        #        So, other message types can be determined here and then
        #        split off.
        parts = msgReg.search(tagless)
        if not parts:
            self.type = None
            return
        else:
            self.type = "msg"

        partsdict = parts.groupdict()
        # Replace HTML entities in the message
        cleanMsg = entityRepl.sub(htmlEntityReplaceFunc, partsdict["message"])
        self.player = partsdict["player"].replace(" ", "_")
        self.msg = cleanMsg
        self.time = None  # TODO: Set receive time here!
        if partsdict["whisper"]:
            if partsdict["whisper"] == "from":
                self.whisper = 0
            else:
                self.whisper = -1
        self.replyTo = self.player if self.whisper == 0 else None
        self.isWhisper = True if self.whisper == 0 else False

    def msgArg(self):
        # Note: This also removes extra spaces and tabs
        return list(filter(lambda x: x and not x.isspace(), self.msg.split(" ")))

    def isCommand(self, prefix="!"):
        # TODO: This should probably be a little more advanced, like check for symbols after
        return True if self.type == "msg" and self.msg[:1] == "!" and self.msg[1:2] != "!" else False

    def noCmdMsg(self):
        return " ".join(self.msgArg()[1:])

    def getArgs(self):
        return self.msgArg()[1:]

    def getCmd(self):
        if not self.isCommand():
            return None
        # From the list of args:
        # - Get the first arg (will be ['!command'])
        # - Get the first element in that list (will be '!command')
        # - Get everything except the first character (will be 'command')
        return self.msgArg()[:1][0][1:]

"""
A library designed to simulate the NEaB chat lib (while providing debugging tools)

@author: Garth
"""
from time import strftime
from .writer import read_log, write_log, full_message


class Profile:
    def __init__(self, username):
        self.username = username

    def auth(self, password):
        return True


class ChatOnline:
    def __init__(self, profile):
        self.profile = profile

    def poll(self, channel):
        pass


class ChatLib:
    def __init__(self, profile):
        self.profile = profile
        self.lastMsgIndex = 0
        self._self_messages = []

    # The messaging functions provide no HTML because it's not needed
    # TODO: At least fake the links and the smilies? (Not that it should matter to Plushie)
    def sendMessage(self, message, to='*'):
        msg = full_message(self.profile.username if to == '*' else "to {:s}".format(to),
                           message)
        self._self_messages.append(msg)

    def _read_external(self):
        self._self_messages.extend(read_log("loop/input.log", True))

    def _write_log(self):
        write_log("loop/output.log", self._self_messages)

    def getRawMessages(self):
        # Make sure to read for new lines
        self._read_external()
        self._write_log()
        res = "<BR>".join(self._self_messages)
        # Log everthing we have so far
        del self._self_messages[:]
        return res

    def getRawMessageList(self):
        message = self.getRawMessages()
        msgList = message.split("<BR>")
        return msgList

    def getMessageList(self):
        ret = []
        for msg in self.getRawMessageList():
            ret.append(Message(msg))
        return ret


def qd(cl):
    ml = cl.getMessageList()
    for m in ml:
        print(m.clean())

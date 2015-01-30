"""
A library designed to simulate the NEaB chat lib (while providing debugging tools)

@author: Garth
"""

from time import strftime

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
        constructed_message = "{:s} {:s}> {:s}".format(
            strftime("%H:%M"),
            self.profile.username if to == '*' else "to {:s}".format(to),
            message
        )
        self._self_messages.append(constructed_message)

    def send_outside_message(self, sender, message, whisper=False):
        """
        External API-like method for simulating sending a message
        """
        constructed_message = "00:00 {:s}> {:s}".format(
            "{:s}{:s}".format("from " if whisper else "", sender),
            message
        )
        self._self_messages.append(constructed_message)

    def send_outside_raw(self, text):
        """
        External API-like method for simulating sending a raw message (can be used to manually send actions)
        """
        self._self_messages.append(text)

    def _read_external(self):
        filename = "loop/test_input.log"
        with open(filename, "r+") as f:
            for line in f:
                stripped = line.rstrip('\n')
                if stripped == "":
                    continue
                self._self_messages.append(stripped)
        # Clear file
        open(filename, "w").close()

    def _write_log(self):
        with open("loop/output.log", "a") as f:
            output = "\n".join(self._self_messages) + "\n"
            f.write(output)

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

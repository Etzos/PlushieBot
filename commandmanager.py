import re


class PluginManager:

    def __init__(self):
        self.plugins = []
        self.commandHooks = []
        self.outputHooks = []
        # Regex
        msgReg = re.compile('(?:\d+\:\d+) (?P<whisper>to|from)? ?' +
                            '(?P<player>[\w\-]+)(?:(?: &gt;)|(?:&gt;)) ' +
                            '(?P<message>.+)')
        tagStrip = re.compile('<[^<]+?>')

    def registerPlugin(self):
        # TODO: Get registered commands
        # TODO: Get output
        pass

    def processMessage(self, message):
        # TODO: Preprocess things like smiley images into text and anchors into the raw URLs
        tagless = self.tagStrip.sub('', message)
        pieces = self.msgReg.search(tagless)
        if not pieces:
            # TODO: Log message and that nothing matched
            return
        parts = pieces.groupdict()

        for p in self.outputHooks:
            p(parts)

        if parts['message'] != '!':
            # TODO: Log, no command in this message
            return

        if " " in parts['message']:
            command, body = parts['message'].split(" ", 1)
        else:
            command = parts['message']
            body = parts['message']

        for p in self.commandHooks:
            p(command, body)
        pass

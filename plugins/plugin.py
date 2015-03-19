
class PlushiePlugin:
    name = "Default Plugin Name"
    description = "Short plugin description"
    authors = []

    def getMethods(self, attrMatch=None):
        for attrName in dir(self):
            attr = getattr(self, attrName)
            if not attrMatch:
                yield attr
            elif hasattr(attr, attrMatch):
                yield attr

    def getCommands(self):
        yield from self.getMethods("isPlushieCommand")

    def getTick(self):
        yield from self.getMethods("isPlushieTick")

    def getMessageHandlers(self):
        yield from self.getMethods("isPlushieMessage")


def plushieCmd(*name, transforms={}):
    def decorator(func):
        func.isPlushieCommand = True
        func.plushieCommand = name
        func.commandTransforms = transforms
        return func
    return decorator


def plushieTick():
    def decorator(func):
        func.isPlushieTick = True
        return func
    return decorator


def plushieMsg():
    def decorator(func):
        func.isPlushieMessage = True
        return func
    return decorator


def commandDoc(cmd=None, alias=(), follows=None, extra=None, doc=""):
    """Decorator for storing documentation (help) for subcommands

    cmd - The command (or subcommand) to be documented
    alias - A tuple containing the possible aliases for the command
    follows - The command (or subcommand) that precedes this command
    extra - Extra parts the follow the command, in short arguments
    doc - The documentation for the command
    All are optional except for "doc"
    """
    def decorator(func):
        if not hasattr(func, '_doc'):
            func._doc = []
        func._doc.append({'cmd': cmd, 'alias': alias, 'follows': follows, 'extra': extra, 'doc': doc})
        return func
    return decorator


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


def plushieCmd(*name):
    def decorator(func):
        func.isPlushieCommand = True
        func.plushieCommand = name
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
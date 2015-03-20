import dbus


class MprisPlaying:
    def __init__(self):
        self.artist = self.title = self.album = self.status = None
        self.metadata = self.playbackstatus = None
        self.bus = dbus.SessionBus()

    def getData(self, interface, path):
        stop = False
        try:
            mpris = self.bus.get_object(interface, path)
        except dbus.exceptions.DBusException:
            stop = True

        if not stop:
            self.metadata = mpris.Get('', 'Metadata')
            self.playbackstatus = mpris.Get('', 'PlaybackStatus')

        if self.metadata:
            self.artist = self.metadata['xesam:artist'][0]
            self.title = self.metadata['xesam:title']
            self.album = self.metadata['xesam:album']
        if self.playbackstatus:
            self.status = self.playbackstatus

    def getArtist(self):
        return self.artist

    def getTitle(self):
        return self.title

    def getAlbum(self):
        return self.album

    def getStatus(self):
        return self.status

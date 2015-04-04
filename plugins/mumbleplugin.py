from .plugin import PlushiePlugin, plushieCmd, commandDoc


class MumblePlugin(PlushiePlugin):
    name = "Mumble Server Details"
    description = "Get the connection details for the Mumble server"
    authors = ["Garth"]

    @plushieCmd("mumble", "voip")
    @commandDoc(doc="Gives the connection details for the Mumble server")
    def run(self, ctx, msg):
        ctx.msg("""The connection details for Garth's Mumble server are:
            [ADDRESS: 184.173.217.82
            PORT: 64588
            PASSWORD: oloc_CEita
            USERNAME: <whatever you want, I recommend your NEaB username>]
            In order to speak be sure to join one of the sub-channels.""",
                msg.replyTo)

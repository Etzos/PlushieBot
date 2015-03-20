from .plugin import PlushiePlugin, plushieCmd, commandDoc

import smtplib


def send_message(config, message, toaddr):
    fromaddr = config["from-address"]
    username = config["username"]
    password = config["password"]
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(username, password)
    server.sendmail(fromaddr, toaddr,
                    "Subject: NEaB Chat\n\n{:s}".format(message))
    server.quit()


class GrabPlugin(PlushiePlugin):
    name = "Grab Plugin"
    description = "Get someone's attention."
    authors = ["Garth"]

    @plushieCmd("grab")
    @commandDoc(extra="<player>", doc="Has Plushie grab <player>'s attention")
    def run(self, ctx, msg):
        target = msg.getArgs()
        playerTargets = ctx.config["grab"]["emails"]

        if len(target) < 1 or not target[0]:
            ctx.msg("I don't know who to grab", msg.replyTo)
        else:
            messaged = False
            plNameLower = target[0].lower()
            if plNameLower in playerTargets.keys():
                messaged = True
                body = "You were grabbed {:s}in NEaB chat!\n{:s}> {:s}".format("(silently) " if msg.isWhisper else "",
                                                                               msg.player,
                                                                               " ".join(target[1:]))
                send_message(ctx.config["grab"], body, playerTargets[plNameLower])
                ctx.msg("{:s} to {:s} sent.".format("Silent message" if msg.isWhisper else "Message",
                                                    target[0]), msg.player)

            if not msg.isWhisper:
                ctx.msg("/me grabs {:s}'s attention".format(target[0]))
                ctx.msg("*glomp* Hey, we want your attention! B(", target[0])
            elif not messaged:
                ctx.msg("If you want to grab someone, don't whisper me.", msg.replyTo)

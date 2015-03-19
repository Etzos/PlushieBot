from .plugin import PlushiePlugin, plushieCmd, commandDoc


class SysPlugin(PlushiePlugin):
    name = "System Stat Plugin"
    description = "A simple plugin for showing certain system statistics"
    authors = ["Garth"]

    @plushieCmd("sys", "system", "sysstats")
    @commandDoc(doc="Returns information about Plushie's server")
    @commandDoc(cmd="battery", alias=("bat",),
                doc="Returns the percentage of Plushie's server's battery and whether it is plugged in or not")
    def base_command(self, ctx, msg):
        args = msg.getArgs()
        arglen = len(args)

        if not arglen:
            ctx.msg("At least one sub-command must be given.", msg.replyTo)
            return

        argone = args[0].lower()
        if argone == "bat" or argone == "battery":
            stat = battery_stats()
            level = float(stat['POWER_SUPPLY_CHARGE_NOW'])/float(stat['POWER_SUPPLY_CHARGE_FULL'])
            plug = "Discharging" if stat['POWER_SUPPLY_STATUS'] == "Discharging" else "Plugged in"
            ctx.msg("The current battery status is {:.1%} ({})".format(level, plug), msg.replyTo)
            return

        ctx.msg("Unknown sub-command '{}'".format(args[0]), msg.replyTo)


def battery_stats():
    """Returns information about the system battery."""
    stuffs = dict()
    with open('/sys/class/power_supply/BAT0/uevent') as f:
        for line in f:
            parts = line.split('=')
            stuffs[parts[0]] = parts[1]
        return stuffs

from .plugin import *

from datetime import datetime, timedelta
from math import floor
from random import sample

import sqlite3


class WerewolfPlugin(PlushiePlugin):
    name = "Werewolf"
    description = "Play a game of werewolf (aka Mafia or Vampire)"
    authors = ["Garth"]

    class Player:
        def __init__(self, name):
            self.name = name
            self.role = "villager"  # Can be: villager, werewolf
            self.voteChoice = None
            self.lastVoteTurn = 0
            self.state = "alive"    # Can be: alive, dead, quit

        def vote(self, player, turn):
            self.voteChoice = player
            self.lastVoteTurn = turn

    class Game:
        def __init__(self):
            # Gamestate
            self.gamestarted = False
            self.players = []
            self.turn = 0
            self.turnChange = datetime.now()
            self.isDay = False
            # Settings
            self.quorum = 5
            self.phaseTime = 90
            self.startTime = 180

    def __init__(self):
        self.gamestarted = False          # Whether a game has started or not
        self.players = []                 # Holds the player objects
        self.turn = 0                     # The current turn (changes every day/night cycle)
        self.turnChange = datetime.now()  # The datetime when the turn has changed
        self.isDay = False                # False when night, True when day (start at night so doPhase() works on start)
        # Settings
        self.quorum = 5                   # Minimum number of players
        self.phaseTime = 90               # Length of each phase (in seconds)
        self.startTime = 180

    @plushieCmd("start")
    @commandDoc(doc="Enters you into a game of Werewolf if one has yet to be started")
    def startCmd(self, ctx, msg):
        # Public ONLY
        args = msg.getArgs()
        numArgs = len(args)

        if msg.isWhisper:
            ctx.msg("Werewolf cannot be started or joined silently. Sorry.", msg.player)
            return

        if any(p for p in self.players if p.name == msg.player):
            ctx.msg("{:s}: You cannot join a game you are already in. ({:s} until game start)"
                    .format(msg.player, self.timeRemainMessage()))
            return

        # Waiting for quorum
        if not self.gamestarted:
            self.resetGame()
            self.gamestarted = True
            self.players.append(self.Player(msg.player))
            ctx.msg("""A new game of werewolf is about to start!
                        Type !start to join.
                        ({:s} until start)""".format(self.timeRemainMessage()))
            ctx.msg(self.quorumMessage())
            ctx.msg("For the instructions/rules use !gamerules", msg.player)
        elif self.gamestarted and self.turn < 1:  # Still in joining phase
            leftTime = self.timeRemainMessage()
            self.players.append(self.Player(msg.player))
            ctx.msg("""You have joined the current game of werewolf!
                        Please await further instructions.
                        ({:s} until start)""".format(
                        self.timeRemainMessage()), msg.player)
            ctx.msg("{:s} ({:s} to join)".format(self.quorumMessage(), leftTime))
            ctx.msg("For the full game instructions/rules use !gamerules", msg.player)
        else:
            ctx.msg("A game of werewolf is already in progress. Please wait for the next game to join")

    @plushieCmd("vote")
    @commandDoc(extra="<player>", doc="Votes for <player> in Werewolf game")
    def voteCmd(self, ctx, msg):
        # MUST be whisper!
        if not msg.isWhisper:
            ctx.msg("The !vote command must be whispered!", msg.player)
            return

        args = msg.getArgs()
        numArgs = len(args)

        if numArgs < 1:
            # TODO: Show possible voting options, be sure to make sure wolves only see solf results
            ctx.msg("You have to supply the name of a player in order to vote.", msg.player)
            return
        if not self.gamestarted or self.gamestarted and self.turn < 1:
            ctx.msg("A game hasn't begun yet, so you cannot vote.", msg.player)
            return
        playerObjGen = [p for p in self.players if p.name == msg.player]
        if not playerObjGen:
            ctx.msg("You are not a part of the current game and therefore cannot vote.", msg.player)
            return
        playerObj = playerObjGen[0]
        if playerObj.state != "alive":
            ctx.msg("You are no longer alive. You cannot vote.", msg.player)
            return

        # At night only the werewolves can vote
        if not self.isDay and playerObj.role != "werewolf":
            ctx.msg("You are not a werewolf, and therefore cannot vote to eliminate someone at night.", msg.player)
            return

        targetLst = [p for p in self.players if p.name.lower() == args[0].lower()]
        if not targetLst:
            ctx.msg("The given player, {:s}, is not playing and cannot be voted for.".format(args[0]), msg.player)
            return
        target = targetLst[0]

        if not self.isDay and target.role == "werewolf":
            ctx.msg("You cannot eliminate your fellow werewolf.", msg.player)
            return

        playerObj.vote(args[0], self.turn)
        ctx.msg("You have voted for {:s} as a {:s}.".format(args[0], playerObj.role), msg.player)

    @plushieCmd("role")
    @commandDoc(doc="Returns whether you are a villager or a werewolf in the Werewolf game")
    def roleCmd(self, ctx, msg):
        # MUST be whisper!
        if not msg.isWhisper:
            ctx.msg("The !role command must be whispered!", msg.player)
            return
        if not self.gamestarted:
            ctx.msg("There is currently no game of Werewolf ongoing. Type !start to start one.", msg.player)
            return

        playerObj = (p for p in self.players if p.name == msg.player)
        if not playerObj:
            ctx.msg("You are not a part of the current game.", msg.player)
            return

        if self.turn < 1:
            ctx.msg("The game hasn't begun, you do not have a role.", msg.player)
        else:
            ctx.msg("Your role is " + playerObj[0].role + ".", msg.player)

    @plushieCmd("players")
    @commandDoc(doc="Returns the players and whether they are alive in the Werewolf game")
    def playersCmd(self, ctx, msg):
        # Whisper OR public
        if not self.gamestarted:
            ctx.msg("There is currently no game of Werewolf ongoing. Type !start to start one.", msg.replyTo)
            return

        if self.turn < 1:
            ctx.msg("Players waiting for game to begin: {:s}".format(", ".join(p.name for p in self.players)),
                    msg.replyTo)
        else:
            ctx.msg("Players in game: {:s}"
                    .format(", ".join((p.name if p.state == "alive" else "{:s} [{:s}]".format(p.name, p.state))
                                      for p in self.players)),
                    msg.replyTo)

    @plushieCmd("gamestat")
    @commandDoc(doc="Returns how many seconds until the next phase of the Werewolf game")
    def gamestatCmd(self, ctx, msg):
        # Whisper OR public
        if not self.gamestarted:
            ctx.msg("There is currently no game of Werewolf ongoing. Type !start to start one.", msg.replyTo)
            return

        if self.turn < 1:
            ctx.msg("There are {:s} until the game starts.".format(self.timeRemainMessage()), msg.replyTo)
        else:
            ctx.msg("There are {:s} until the next phase change. {:s}".format(self.timeRemainMessage(),
                                                                              self.phaseMessage(False)),
                    msg.replyTo)

    @plushieCmd("forceturn")
    @commandDoc(doc="Currently is just a place holder command")
    def forceTurn(self, ctx, msg):
        ctx.msg("Blah")

    @plushieCmd("gamerules")
    @commandDoc(doc="Returns the game rules for the Werewolf game")
    def gamerulesCmd(self, ctx, msg):
        ctx.msg(self.instructionsMessage(), msg.player)

    @plushieTick()
    def tick(self, ctx):
        # Check for phase change
        timeDiff = datetime.now() - self.turnChange
        time = self.phaseTime if self.gameBegun() else self.startTime

        # Time for a phase change!
        if self.gamestarted and timeDiff.total_seconds() >= time:
            # Ready to start!
            if self.turn == 0:
                if len(self.players) < self.quorum:
                    ctx.msg("Not enough players have joined to start a game in time. Resetting.")
                    self.resetGame()
                else:
                    ctx.msg("A game of werewolf has just started!")
                    # set roles
                    numwolves = floor(len(self.players)*0.3)
                    wolves = sample(self.players, numwolves)
                    for p in wolves:
                        p.role = "werewolf"
                    # Tell player's their role
                    wolfstring = ", ".join(w.name for w in wolves)
                    for p in self.players:
                        ctx.msg("You are a " + p.role + ".", p.name)
                        if p.role == "werewolf":
                            ctx.msg("Your fellow werewolves are: {:s}".format(wolfstring,), p.name)
                    # Start the current phase
                    self.doPhase(ctx, isStart=True)
            else:
                self.doPhase(ctx)

    # == Helper Methods == #
    def resetGame(self):
        self.gamestarted = False
        self.players = []
        self.turn = 0
        self.turnChange = datetime.now()
        self.isDay = False

    def doPhase(self, ctx, isStart=False):
        # Check for game over conditions
        if not isStart:
            oldPlayers = []
            killVote = dict()
            for p in self.players:
                # Eliminate old players
                if self.turn - p.lastVoteTurn >= 2:
                    p.state = "quit"
                    oldPlayers.append(p)
                    continue
                # Don't add empty votes
                if not p.voteChoice:
                    continue
                if p.voteChoice in killVote:
                    killVote[p.voteChoice] += 1
                else:
                    killVote[p.voteChoice] = 1
                # Reset vote
                p.voteChoice = None

            if not killVote:
                # TODO: No players left to play, game over
                if not self.isDay:
                    ctx.msg("No werewolves have voted this round. The game ends with the villagers winning by default!")
                else:
                    ctx.msg("No players have voted. The game ends in a draw.")
                ctx.msg(self.finalStatsMessage())
                self.resetGame()
                return
            orderedVotes = sorted(killVote.items(), key=lambda x: x[1], reverse=True)
            print("Ordered Votes:")
            print(orderedVotes)
            top = orderedVotes[0]
            print("Top:")
            print(top)
            toKill = sample([x for x in orderedVotes if x[1] == top[1]], 1)[0]

            # Check win/loss conditions with toKill and old players removed
            print("To Kill:")
            print(toKill)
            pl = [x for x in self.players if x.name.lower() == toKill[0].lower()]
            print("Player selected:")
            print(pl)
            pl[0].state = "dead"

            # Count remaning villagers and werewolves
            villagers = werewolves = 0
            for p in self.players:
                if p.state != "alive":
                    continue
                if p.role == "werewolf":
                    werewolves += 1
                elif p.role == "villager":
                    villagers += 1
            # NOTE: If the current phase is day, then the next phase will be night.
            #       With only two players, that means that werewolves win.
            if self.isDay and len(self.players) == 2:
                ctx.msg("There is only one villager and one werewolf left, and night is about to fall. The villagers "
                        "are doomed!")
                for p in self.players:
                    if p.role == "village" and p.state == "alive":
                        p.state = "dead"
                ctx.msg(self.finalStatsMessage())
                self.resetGame()
                return
            elif werewolves == 0:
                # Villagers win
                ctx.msg("The villagers have eliminated all of the werewolves! Villagers win!")
                ctx.msg(self.finalStatsMessage())
                self.resetGame()
                return
            elif werewolves > villagers:
                # werewolves win
                ctx.msg("The werewolves outnumber the villagers! Werewolves win!")
                ctx.msg(self.finalStatsMessage())
                self.resetGame()
                return
            else:
                ctx.msg("You have been eliminated from the game. Sorry.", pl[0].name)
                ctx.msg("{:s} has been eliminated by the {:s}! {:s}".format(
                        pl[0].name, "villagers" if self.isDay else "werewolves",
                        " Quit: " + ", ".join(oldPlayers) if len(oldPlayers) > 0 else ""))

        if self.isDay:
            self.isDay = False
        else:
            self.isDay = True
            self.turn += 1
        self.turnChange = datetime.now()
        ctx.msg(self.phaseMessage())

    def gameBegun(self):
        return True if self.gamestarted and self.turn > 0 else False

    # == Message Generation Methods == #
    def quorumMessage(self):
        num = len(self.players)
        diff = self.quorum - num
        if diff == 0:
            return "Quorum of " + str(num) + " players reached!"
        elif diff == self.quorum-1:  # Handle the singular
            return "There is currently 1 player. Need {:d} more for quorum.".format(diff)
        elif diff > 0:
            return "There are currently {:d} players. Need {:d} more for quorum.".format(num, diff)
        else:
            return "There are currently {:d} players. More than enough!".format(num)

    def phaseMessage(self, includeInst=True):
        ret = "It is now {:s} of turn {:d}.".format("day" if self.isDay else "night", self.turn)
        if includeInst:
            ret += """ {:s} should cast their vote using
                      `/msg Plushie !vote <Player Name (Case Important!)>`""".format(
                          "Everyone" if self.isDay else "Werewolves")
        return ret

    def finalStatsMessage(self):
        return "Villagers: {:s}. Werewolves: {:s}.".format(
                ", ".join("{:s} [{:s}]".format(p.name, p.state) for p in self.players if p.role == "villager"),
                ", ".join("{:s} [{:s}]".format(p.name, p.state) for p in self.players if p.role == "werewolf")
            )

    def timeRemainMessage(self):
        diff = datetime.now() - self.turnChange
        time = self.phaseTime if self.gameBegun() else self.startTime
        return "{:d} seconds remaining".format(time - diff.total_seconds())

    def instructionsMessage(self):
        return """
        You have decided to join a game of Werewolf (if not, do it now use `!start`). If you don't know how to play, the
        rules will be explained here.
        The rules are pretty simple:
        There are two groups that will be chosen randomly when the game starts, the villagers and the werewolves.
        Only the werewolves know who the other werewolves are. Villagers don't know who is a werewolf and who is a
        villager.
        VILLAGERS can only vote during the day and their task is to eliminate all of the werewolves.
        WEREWOLVES get to act during the day and night. During the day, they act like a villager and pick someone to
        eliminate.
        However, at night they get to vote again to choose a villager to eliminate.
        GAMEPLAY: The game starts on turn 1 day. Everyone (villagers and werewolves) vote to eliminate a player. After
        90 seconds The votes are tallied
        The player with the most votes is eliminated (or if there is a tie, the game will decide who to eliminate), and
        it changes from turn 1 day to
        turn 1 night. During the night phase, only werewolves can vote. The same voting mechanics apply as during the
        day and gameplay continues with turn 2 day.
        WINNING: For villagers to win, all werewolves must be eliminated. For werewolves to win, there must be fewer
        villagers than werewolves.
        """

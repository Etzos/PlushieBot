from .plugin import PlushiePlugin, plushieCmd, commandDoc, plushieTick

import datetime
import random


class Challenge:
    ROCK, PAPER, SCISSORS, LIZARD, SPOCK = range(5)
    TYPICAL, EXTENDED = range(2)
    challenger = None
    target = None
    challengerChoice = None
    targetChoice = None
    initiated = None

    def __init__(self, player, target, gametype=TYPICAL):
        self.challenger = player
        self.target = target
        self.initiated = datetime.datetime.now(datetime.timezone.utc)
        self.gametype = gametype


class RPSPlugin(PlushiePlugin):
    name = "Rock Paper Scissors Plugin"
    description = "Allows players to play a game of Rock Paper Scissors (Rock Paper Scissors)"
    authors = ["Garth"]

    def __init__(self):
        self.challenges = []
    #    self.db = sqlite3.connect("rps.db")
    #
    #    self.db.execute("""
    #        CREATE TABLE IF NOT EXISTS challenge (
    #        id INTEGER PRIMARY KEY AUTOINCREMENT,
    #        challenger INTEGER REFRENCES player(id) ON UPDATE CASCASE,
    #        challengerChoice INTEGER,
    #        target INTEGER REFRENCES player(id) ON UPDATE CASCADE,
    #        targetChoice INTEGER,
    #        challengeTime TEXT
    #        )""")
    #
    #    self.db.execute("""
    #        CREATE TABLE IF NOT EXISTS player (
    #        id INTEGER PRIMARY KEY AUTOINCREMENT,
    #        name TEXT NOT NULL,
    #        normalizedName TEXT NOT NULL,
    #        win INTEGER DEFAULT 0,
    #        loss INTEGER DEFAULT 0
    #        )""")
    #    self.db.commit()

    def pickWinner(self, choiceOne, choiceTwo):
        # -1 = one won
        # 0 = tie
        # 1 = two won
        if choiceOne == Challenge.ROCK:
            if choiceTwo == Challenge.ROCK:
                return 0
            elif choiceTwo == Challenge.PAPER:
                return 1
            elif choiceTwo == Challenge.SCISSORS:
                return -1
        elif choiceOne == Challenge.PAPER:
            if choiceTwo == Challenge.ROCK:
                return -1
            elif choiceTwo == Challenge.PAPER:
                return 0
            elif choiceTwo == Challenge.SCISSORS:
                return 1
        elif choiceOne == Challenge.SCISSORS:
            if choiceTwo == Challenge.ROCK:
                return 1
            elif choiceTwo == Challenge.PAPER:
                return -1
            elif choiceTwo == Challenge.SCISSORS:
                return 0
        else:
            raise RuntimeError("Unknown input.")

    def getChoice(self, convert):
        convert = convert.lower()
        if convert == "rock":
            return Challenge.ROCK
        elif convert == "paper":
            return Challenge.PAPER
        elif convert == "scissors":
            return Challenge.SCISSORS
        else:
            raise RuntimeError("Unknown input: {:s}".format(convert))

    def randomChoice(self):
        return random.choice([Challenge.ROCK, Challenge.PAPER, Challenge.SCISSORS])

    def printableChoice(self, choice):
        if choice == Challenge.ROCK:
            return "rock"
        elif choice == Challenge.PAPER:
            return "paper"
        elif choice == Challenge.SCISSORS:
            return "scissors"
        raise RuntimeError("Unknown choice.")

    @plushieCmd("challenge")
    @commandDoc(extra="[rock|paper|scissor]", doc="Plays a game of rock-paper-scissors with Plushie")
    def challenge(self, ctx, msg):
        args = msg.getArgs()
        arglen = len(args)
        if arglen < 1:
            ctx.msg("You must provide an argument.", msg.replyTo)
            return

        try:
            playerChoice = self.getChoice(args[0])
        except RuntimeError:
            ctx.msg("Unknown type: {:s}".format(args[0]))
            return

        plushieChoice = self.randomChoice()
        reply = "Plushie chooses {:s}.".format(self.printableChoice(plushieChoice))

        result = self.pickWinner(playerChoice, plushieChoice)
        if result > 0:
            ctx.msg("{:s} Plushie wins against {:s}.".format(reply, msg.player), msg.replyTo)
        elif result < 0:
            ctx.msg("{:s} {:s} wins against Plushie.".format(reply, msg.player), msg.replyTo)
        else:
            ctx.msg("{:s} No one wins.".format(reply), msg.replyTo)

    @plushieTick()
    def cleaner(self, ctx):
        pass

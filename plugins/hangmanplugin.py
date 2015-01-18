from .plugin import *

import urllib.request
import urllib.parse
import json


class HangmanPlugin(PlushiePlugin):
    name = "Hangman Plugin"
    description = "Play a game of hangman"
    authors = ["Garth", "WhiteKitsune"]

    def __init__(self):
        self.word = None
        self.guessedLetters = []
        self.misses = 0
        self.maxMisses = 9

    @plushieCmd("hangman")
    def startGame(self, ctx, msg):
        args = msg.getArgs()

        if msg.isWhisper:
            if len(args) < 1:
                    ctx.msg("Not enough arguments. Please choose the game mode(Public/Private) and give me only one word for everyone to guess.", msg.player)
                    return
            if len(args) > 2:
                ctx.msg("Too many arguments. Please choose the game mode(Public/Private) and give me only one word for everyone to guess.", msg.player)
                return

            if args[0].lower() == "private":
                ctx.msg("You cannot play hangman solely from whisper... Yet.", msg.player)
                return
            elif args[0].lower() == "public":
                if len(args) < 2:
                    ctx.msg("Not enough arguments. Please choose the game mode(Public/Private) and give me only one word for everyone to guess.", msg.player)
                    return
                if not args[1].isalpha():
                    ctx.msg("The word you have told me contains characters other than letters. Please only use letters.", msg.player)
                    return

                if not self.word:
                    self.word = args[1]
                    # Make sure settings are back to beginning
                    self.guessedLetters = []
                    self.misses = 0
                    ctx.msg("{:s} has given me a word. Try guessing some letters! (!guess <letter>)".format(msg.player))
                else:
                    ctx.msg("A game of hangman is already in progress, use `!guess <letter>` to guess.", msg.player)
            else:
                ctx.msg("Please choose from either Public or Private game modes.", msg.player)
                return

        if not self.word:
            try:
                word = HangmanPlugin.getWord(ctx.config["hangman"]["api-key"])
            except:
                ctx.msg("Unable to get a new word. Try again later.")
                return
            self.word = word
            # Make sure settings are back to beginning
            self.guessedLetters = []
            self.misses = 0
            ctx.msg("I've thought of a word, try guessing some letters! (!guess <letter>)")
            ctx.msg(self.displayStatus())
        else:
            #ctx.msg("A game of hangman is already in progress, use `!guess <letter>` to guess.")
            ctx.msg(self.displayStatus())

    @plushieCmd("guess")
    def guessLetter(self, ctx, msg):
        args = msg.getArgs()

        if not self.word:
            ctx.msg("A game hasn't been started, use !hangman to start a game.", msg.replyTo)
            return
        if len(args) < 1:
            ctx.msg("Please guess a letter.", msg.replyTo)
            return
        # Convert chat stupidity
        if args[0] == "you":
            args[0] = "u"
        elif args[0] == "okay":
            args[0] = "k"
        elif args[0] == "are":
            args[0] = "r"
        elif args[0] == "see":
            args[0] = "c"
        elif args[0] == "why":
            args[0] = "y"
        if len(args[0]) > 1:
            #TODO: Guess entire word
            ctx.msg("You guessed more than a letter! Try again with only one.", msg.replyTo)
            return
        if not args[0].isalpha():
            ctx.msg("The character you guessed is not a letter. Please guess a letter.", msg.replyTo)
            return

        guess = args[0].lower()
        word = self.word.lower()
        if guess in self.guessedLetters:
            ctx.msg("You have already guessed the letter '{:s}'".format(args[0]), msg.replyTo)
            ctx.msg(self.displayStatus(), msg.replyTo)
            return

        self.guessedLetters.append(guess)
        if guess in word:
            if self.wordComplete():
                ctx.msg("Congratulations, you guessed the word: {:s}!".format(self.word), msg.replyTo)
                if msg.isWhisper:
                    ctx.msg("{:s} has guessed the word {:s}!".format(msg.player, self.word))
                self.word = None
                self.guessedLetters = []
                self.misses = 0
            else:
                ctx.msg(self.displayStatus(), msg.replyTo)
        else:
            self.misses += 1
            if self.misses >= self.maxMisses:
                ctx.msg("You have guessed incorrectly too many times. Game over. The word was: {:s}.".format(self.word), msg.replyTo)
                if msg.isWhisper:
                    ctx.msg("{:s} has attempted to guess the word to many times. The word was: {:s}.".format(msg.player, self.word))
                self.word = None
                self.guessedLetters = []
                self.misses = 0
            else:
                ctx.msg(self.displayStatus(), msg.replyTo)

    @plushieCmd("word", "getword")
    def printWord(self, ctx, msg):
        try:
            print(ctx.config["hangman"]["api-key"])
            word = HangmanPlugin.getWord(ctx.config["hangman"]["api-key"])
        except:
            word = "No word."
        ctx.msg("Your word is: {:s}".format(word), msg.replyTo)

    def displayStatus(self):
        return "{:s} [ {:s}{:s} | {:d}:{:d} ] {{{:s}}}".format(
            self.wordDisplay(),
            "X"*self.misses, "@"*(self.maxMisses-self.misses),
            self.misses, self.maxMisses,
            ", ".join(sorted([l+"*" if l in self.word else l for l in self.guessedLetters]))
            )

    def wordDisplay(self):
        res = ""
        for l in self.word:
            if l.lower() in self.guessedLetters:
               res += l
            else:
                res += "-"
        return res

    def wordComplete(self):
        for l in self.word:
            if not l.lower() in self.guessedLetters:
                return False
        return True

    @staticmethod
    def getWord(api_key, minCorpus=6000, maxCorpus=-1, minLength=5, maxLength=20):
        siteURL = "http://api.wordnik.com/v4/words.json/randomWord"
        paramaters = urllib.parse.urlencode({
            "hasDictionaryDef": True,
            "includePartOfSpeech": "noun",
            "minCorpusCount": minCorpus,
            "maxCorpusCount": maxCorpus,
            "minDictionaryCount": 0,
            "maxDictionaryCount": -1,
            "minLength": minLength,
            "maxLength": maxLength,
            "api_key": api_key
        })
        res = urllib.request.urlopen(siteURL + "?{:s}".format(paramaters))
        jobj = res.read().decode('utf-8')
        jparse = json.loads(jobj)
        return jparse['word']
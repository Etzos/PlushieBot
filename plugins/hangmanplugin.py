from .plugin import *

import urllib.request
import urllib.parse
import json


class HangmanPlugin(PlushiePlugin):
    name = "Hangman Plugin"
    description = "Play a game of hangman"
    authors = ["Garth", "WhiteKitsune", "Arik1"]

    def __init__(self):
        self.word = None
        self.guessedLetters = []
        self.misses = 0
        self.maxMisses = 9

    @plushieCmd("hangman")
    @commandDoc(doc="Starts a game of hangman")
    @commandDoc(cmd="public", extra="<word>",
                doc="Starts a game of hangman where the word is the <word> of your choice")
    @commandDoc(cmd="private", extra="<word>", doc="Currently does nothing")
    def startGame(self, ctx, msg):
        args = msg.getArgs()

        if msg.isWhisper:
            if len(args) < 1:
                    ctx.msg("Not enough arguments. Please choose the game mode(Public/Private) and give me some "
                            "word(s) for everyone to guess.", msg.player)
                    return

            if args[0].lower() == "private":
                ctx.msg("You cannot play hangman solely from whisper... Yet.", msg.player)
                return
            elif args[0].lower() == "public":
                if len(args) < 2:
                    ctx.msg("Not enough arguments. Please choose the game mode(Public/Private) and give me some "
                            "word(s) for everyone to guess.", msg.player)
                    return
                badwords = 0
                for arg in args[1:]:
                    if not arg.isalpha():
                        ctx.msg("The word you have told me contains characters other than letters. Please only use "
                                "letters.", msg.player)
                        return
                    if not HangmanPlugin.checkWord(ctx.config["hangman"]["api-key"], arg):
                        badwords += 1

                if not self.word:
                    self.word = " ".join(args[1:])
                    self.guessedLetters = []
                    self.misses = 0
                    # Make sure settings are back to beginning
                    ctx.msg("{:s} has given me a {:s}. Try guessing some letters! (!guess <letter>)"
                            .format(msg.player, "word" if len(args) <= 2 else "phrase"))

                    if badwords == 1:
                        ctx.msg("There was 1 'word' that was not found in Wordnik!")
                    else:
                        if badwords > 1:
                            ctx.msg("There were {:d} 'words' that were not found in Wordnik!".format(badwords))
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
            # ctx.msg("A game of hangman is already in progress, use `!guess <letter>` to guess.")
            ctx.msg(self.displayStatus())

    @plushieCmd("guess")
    @commandDoc(extra="<letter>", doc="Guesses a <letter> for the Hangman game")
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
            # TODO: Guess entire word
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
                ctx.msg("You have guessed incorrectly too many times. Game over. The word was: {:s}."
                        .format(self.word), msg.replyTo)
                if msg.isWhisper:
                    ctx.msg("{:s} has attempted to guess the word to many times. The word was: {:s}."
                            .format(msg.player, self.word))
                self.word = None
                self.guessedLetters = []
                self.misses = 0
            else:
                ctx.msg(self.displayStatus(), msg.replyTo)

    @plushieCmd("word", "getword")
    @commandDoc(doc="Returns a word")
    def printWord(self, ctx, msg):
        try:
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
            if l.lower() in self.guessedLetters or l == " ":
                res += l
            else:
                res += "-"
        return res

    def wordComplete(self):
        for l in self.word:
            if l == " ":
                continue
            if not l.lower() in self.guessedLetters:
                return False
        return True

    @staticmethod
    def getWord(api_key, minCorpus=6000, maxCorpus=-1, minLength=5, maxLength=20):
        siteURL = "http://api.wordnik.com/v4/words.json/randomWord"
        parameters = urllib.parse.urlencode({
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
        res = urllib.request.urlopen("{:s}?{:s}".format(siteURL, parameters))
        jobj = res.read().decode('utf-8')
        jparse = json.loads(jobj)
        return jparse['word']

    @staticmethod
    def checkWord(api_key, word, minCorpus=5, maxCorpus=-1, minLength=1, maxLength=-1):
        siteURL = "http://api.wordnik.com/v4/words.json/search"
        parameters = urllib.parse.urlencode({
            "minCorpusCount": minCorpus,
            "maxCorpusCount": maxCorpus,
            "minDictionaryCount": 0,
            "maxDictionaryCount": -1,
            "minLength": minLength,
            "maxLength": maxLength,
            "api_key": api_key,
            "caseSensitive": False
        })
        res = urllib.request.urlopen("{:s}/{:s}?{:s}".format(siteURL, word, parameters))
        jobj = res.read().decode('utf-8')
        jparse = json.loads(jobj)
        return not jparse['totalResults'] == 0

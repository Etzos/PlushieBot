# PlushieBot

[![Travis](https://img.shields.io/travis/Etzos/PlushieBot.svg)](https://travis-ci.org/Etzos/PlushieBot)
[![Coveralls](https://img.shields.io/coveralls/Etzos/PlushieBot.svg)](https://coveralls.io/r/Etzos/PlushieBot)


## Running

In order to run PlushieBot for yourself you'll need to modify a few things
first. Unfortunately I haven't included the library to actually connect to
NEaB chat. However, I did add a "server" of sorts that can be run locally on
your computer. I'm assuming you already have python (at least version 3.2)
installed on your computer. In order to use this server you must:

* Copy the config.json.example file to config.json and edit the contained values
* Make a call to the bot runner program: `python botrunner.py --debug` (NOTE:
  You don't *have* to run in debug mode, but it makes things easier)
* Run the testing console (you *MUST* do this from the loop/ directory):
  `python testconsole.py`

### Linux Users
I have provided a fancy wrapper script (called `runplushie.sh`) that will
launch both Plushie and the testing console for you. All the arguments are
passed through except for the `-c` or `--console` flags which are used to
start the testing console before launching Plushie in the console. Note that
the script *must* be called from Plushie's top-level directory.

### Windows Users
There is a batch script for Windows users (called `testplushie.bat`) that will
launch Plushie and the testing console automatically. It does not, however,
pass arguments through to the Plushie launching program, so you may have to
modify it a bit if you want it to work differently than the default
configuration.

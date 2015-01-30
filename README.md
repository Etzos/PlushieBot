# Running PlushieBot #

In order to run PlushieBot for yourself you'll need to modify a few things
first. Unfortunately I haven't included the library to actually connect to
NEaB chat. However, I did add a "server" of sorts that can be run locally on
your computer. I'm assuming you already have python (at least version 3)
installed on your computer. In order to use this server you must:

* Copy the config.json.example file to config.json and edit the contained values
* Comment out `from lib import Profile, ChatLib, ChatOnline` and uncomment
  `from loop.lib import Profile, ChatLib, ChatOnline`
* Run the plushieprocess.py file (`python plushieprocess.py` from a command line in that directory)
* Navigate to the `loop/` directory and run the testconsole.py file (same way as the above)
* Hope all goes well

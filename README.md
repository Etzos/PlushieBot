# Running PlushieBot #

In order to run PlushieBot for yourself you'll need to modify a few things
first. Unfortunately I haven't included the library to actually connect to
NEaB chat. However, I did add a "server" of sorts that can be run locally on
your computer. I'm assuming you already have python (at least version 3)
installed on your computer. In order to use this server you must:

* Copy the config.json.example file to config.json and edit the contained values
* Plushie is set to use the Loopback server by default
* Comment out `from lib import Profile, ChatLib, ChatOnline` and uncomment
  `from loop.lib import Profile, ChatLib, ChatOnline`
* For Windows only: In plushieprocess.py change `from multiprocessing import Process, Pipe` to `from multiprocessing.dummy import Process, Pipe`
* Run the plushieprocess.py file (`python plushieprocess.py` from a command line in that directory)
* Navigate to the `loop/` directory and run the testconsole.py file (same way as the above)
* Hope all goes well

* I have included a batch file for Windows users to start both the server and Plushie. Leave it in the current directory.
* Pester Garth for the Linux version :P

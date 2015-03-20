#!/usr/bin/env python
"""
This file is responsible for setting up the bot's event loop and
passing messages from the network loop into Plushie, which will
be run outside of the loop.
"""
import json


def loadConfig(name="config.json"):
    conf = open(name, "r")
    return json.loads(conf.read())

if __name__ == "__main__":
    import argparse
    import sys

    from plushiecore import run_plushie
    from botnetwork import run_network

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="run Plushie in debug mode (loopback server)", action="store_true")
    parser.add_argument("-t", "--thread", help="run Plushie using threads instead of processes", action="store_true")
    args = parser.parse_args()

    subargs = {}
    if args.debug:
        subargs['debug'] = True
    if args.thread:
        from multiprocessing import Process, Queue, Pipe
    else:
        from multiprocessing.dummy import Process, Queue, Pipe

    try:
        config = loadConfig()
    except:
        print("Loading config file failed. Dying.")
        sys.exit(1)

    # Messages should be as follows:
    # ('type', 'message')
    # Where 'type' will be one of: 'system', 'chat' and 'message' will be the message to be used
    net_in = Queue()   # Messages to send to NEaB
    net_out = Queue()  # Messages from NEaB

    network_process = Process(target=run_network, args=(config, net_in, net_out, subargs))
    plushie_process = Process(target=run_plushie, args=(config, net_in, net_out))

    network_process.start()
    plushie_process.start()

    while True:
        r = input("> ")
        if r == "exit" or r == "stop":
            print("Stopping PlushieBot...")
            net_in.put(('system', 'stop'))
            network_process.join()
            plushie_process.join()
            break

    print("Stopped.")
    network_process.join()
    plushie_process.join()
    sys.exit(0)

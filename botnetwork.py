import time
import queue


def run_network(config, inputs, outputs, args):
    # Ugly! But it should work
    if args['debug']:
        from loop.lib import Profile, ChatLib, ChatOnline
    else:
        try:
            from lib import Profile, ChatLib, ChatOnline
        except:
            from loop.lib import Profile, ChatLib, ChatOnline

    botProfile = Profile(config["username"])
    isAuth = botProfile.auth(config["password"])
    if not isAuth:
        print("Unable to auth properly.")
        # TODO: Send a message using p to tell main process that we're dying
        outputs.send(('system', 'stop'))
        return

    c = ChatLib(botProfile)
    o = ChatOnline(botProfile)

    # TODO: REFACTOR
    try:
        # Bring the last message up to date
        c.getRawMessages()
        # Put self in online list
        o.poll(0)
    except:
        print("Error attempting to start: Unable to do first poll. Process dying.")
        return
    # END REFACTOR

    # This loop was basically copied from plushiecode.py
    current_time = time.time()
    previous_time = current_time
    wait_time = 4 if not args['debug'] else 1  # in seconds
    current_wait_time = wait_time  # Amount of time to wait between polls
    iterations = 0  # The number of iterations gone through for polling (used for deciding when to poll online list)
    bad_polls = 0  # Number of times polling the server failed (used to calculate current_wait_time)
    while True:
        current_time = time.time()
        timediff = current_time - previous_time

        if timediff >= current_wait_time:
            previous_time = current_time
            try:
                msgs = c.getRawMessageList()
                if iterations > 1:
                    iterations = 0
                    o.poll(0)
                else:
                    iterations += 1
            except:
                print("Bad connection of some sort")
                bad_polls += 1
                current_wait_time = wait_time * bad_polls
                continue

            bad_polls = 0

            for msg in msgs:
                if not msg:
                    continue
                outputs.put(('chat', msg))

        try:
            message = inputs.get(True, max(current_wait_time - timediff, 0))
        except queue.Empty:
            continue

        if message[0] == 'system':
            if message[1] == 'stop':
                outputs.put(('system', 'stop'))
                break
            else:
                print("Unknown system message " + message[1])
        elif message[0] == 'chat':
            c.sendMessage(message[1])
        else:
            print("Unknown message type '" + message[0] + "'")

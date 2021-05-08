def initilize():
    global config
    global updated
    global lockedWindow

    config = {}
    updated = False
    lockedWindow = False

    logging.debug("Config loaded")

def __isTrue(value):
    return bool(value == "1")
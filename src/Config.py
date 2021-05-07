def initilize():
    global config
    global updated
    global lockedWindow

    config = {}
    updated = False
    lockedWindow = False

def __isTrue(value):
    return bool(value == "1")
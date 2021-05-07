import logging
import keyboard

import Config


callbacks = dict()

def registerCallback(type, cb):

    if callbacks.get(type, None):
        callbacks[type].append(cb)
    else:
        callbacks[type] = [cb]

def setupHotkeys():

    logging.debug("Setting up Hotkeys")

    keyboard.unhook_all()
    hotkeyConfig = Config.config["HOTKEYS"]

    for hk in hotkeyConfig.keys():
        logging.debug(f"{hotkeyConfig[hk]}:  {hk}")
        keyboard.add_hotkey(hotkeyConfig[hk], handleHotkey, args=(hk, ))


def handleHotkey(type):
    logging.debug(f"hotkey {type}")
    
    cbs = callbacks.get(type, lambda: None)
    for cb in cbs:
        cb()


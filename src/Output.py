import logging
import time

import Config

import Keystroke
import KeyCodeMap

lastDetect = 0
lastFreeFish = 0
lastFishingStart = 0
state = False


def __performFishOutput():
    for i in range(int(Config.config["INPUTS"].get("fishDetectAmmount", 1))):
        Keystroke.anyKey(
            Config.config["INPUTS"].get("onFishDetect", ""))


def __performFishingStart():
    global lastDetect
    global lastFreeFish
    global lastFishingStart
    global state

    now = time.time()
    lastFishingStart = now

    if (now - lastFreeFish) >= int(Config.config["INPUTS"].get("fishingFreeTimeout", 10000)):
        logging.debug("Starting free fishing")
        lastFreeFish = now
        Keystroke.anyKey(Config.config["INPUTS"].get("initiateFishingFree", ""))
    else:
        logging.debug("Starting normal fishing")
        Keystroke.anyKey(Config.config["INPUTS"].get("initiateFishingNormal", ""))


def resetFishingState():
    global lastDetect
    global lastFreeFish
    global lastFishingStart
    global state

    time.sleep(1)   # if initiated via hotkeys, let user depress meta keys before input

    lastDetect = time.time()
    lastFreeFish = 0
    lastFishingStart = 0
    state = "idle"


def onFishDetect():
    global lastDetect
    global lastFreeFish
    global lastFishingStart
    global state

    now = time.time()

    # catch duration
    if state == "fishing" and ((now - lastDetect) >= int(Config.config["INPUTS"].get("catchDuration", 6))):
        logging.debug("Catching fish")
        lastDetect = now
        state = "catching"
        __performFishOutput()


def initiateFishing():
    global lastDetect
    global lastFreeFish
    global lastFishingStart
    global state

    now = time.time()

    # if we're idle then restart fishing
    if state == "idle":
        logging.debug("Starting fishing")
        state = "fishing"

        __performFishingStart()

    elif (state == "catching") and \
            ((now - lastDetect) >= (int(Config.config["INPUTS"].get("catchDuration", 6)) + 2)): # catch duration + padding
        logging.debug("Fishing detection timeout")
        state = "idle"

    elif (state != "idle") and \
            ((now - lastFishingStart) >= int(Config.config["INPUTS"].get("fishingTimeout", 30))): # max fishing duration
        logging.debug("Fishing start timeout")
        state = "idle"

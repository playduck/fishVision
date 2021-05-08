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
        Keystroke.keyCombination(
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
        #Keystroke.keyCombination(Config.config["INPUTS"].get("initiateFishingFree", ""))
    else:
        logging.debug("Starting normal fishing")
        #Keystroke.keyCombination(Config.config["INPUTS"].get("initiateFishingNormal", ""))


def resetFishingState():
    global lastDetect
    global lastFreeFish
    global lastFishingStart
    global state

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
        logging.debug("catching fish")
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
        logging.debug("starting fishing")
        state = "fishing"

        __performFishingStart()

    elif (state == "catching") and \
            ((now - lastDetect) >= (int(Config.config["INPUTS"].get("catchDuration", 6)) + 2)):            # catch duration + padding
        logging.debug("fishing detection timeout")
        state = "idle"

    elif (state != "idle") and \
            ((now - lastFishingStart) >= int(Config.config["INPUTS"].get("fishingTimeout", 30))):           # max fishing duration
        logging.debug("fishing start timeout")
        state = "idle"

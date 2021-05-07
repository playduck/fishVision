import logging
import time

import Config

import Keystroke
import KeyCodeMap

lastDetect = 0
lastFreeFish = 0


def resetFishingState():
    global lastDetect
    global lastFreeFish

    lastDetect = time.time()
    lastFreeFish = 0


def onFishDetect():
    global lastDetect
    global lastFreeFish

    now = time.time()
    if (now - lastDetect) >= int(Config.config["INPUTS"].get("afterFishTimeout", 0)):
        lastDetect = now

        logging.debug("Detected Fish")
        for i in range(int(Config.config["INPUTS"].get("fishDetectAmmount", 1))):
            Keystroke.keyCombination(
                Config.config["INPUTS"].get("onFishDetect", ""))



def initiateFishing():
    global lastDetect
    global lastFreeFish

    now = time.time()

    # only initiate if we're after the last detection timeout
    if (now - lastDetect) >= int(Config.config["INPUTS"].get("afterFishTimeout", 0)):
        # if we're past the free fishing timeout, use that
        if (now - lastFreeFish) >= int(Config.config["INPUTS"].get("fishingFreeTimeout", 10000)):
            logging.debug("Starting free fishing")
            lastFreeFish = now
            #Keystroke.keyCombination(Config.config["INPUTS"].get("initiateFishingFree", ""))
        else:
            logging.debug("Starting normal fishing")
            #Keystroke.keyCombination(Config.config["INPUTS"].get("initiateFishingNormal", ""))

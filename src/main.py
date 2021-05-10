#!/usr/bin/env python3

import logging
import atexit
import threading
import time
from signal import signal, SIGINT
import sys

import Config
import InIReader

import Keystroke
import KeyCodeMap

import Hotkeys

import Capture
import Output

threads = list()
iniReaderPill = threading.Event()
capturePill = threading.Event()
mainPill = threading.Event()
started = False

def exitHandler(*args):
    while 1:
        logging.debug("Setting Pill")
        iniReaderPill.set()
        capturePill.set()
        mainPill.set()

        for thread in threads:
            logging.debug(f"Joining Thread {thread}")
            thread.join()

        logging.debug("Exiting")
        sys.exit()


def startCapture():
    logging.debug("Starting Capture")
    capturePill.clear()

    cap = threading.Thread(
        target=Capture.capture, args=(capturePill,))
    threads.append(cap)
    cap.start()
    started = True


def stopCapture():
    logging.debug("Stopping Capture")
    capturePill.set()
    started = False


def toggleLockedWindow():
    Config.lockedWindow = not Config.lockedWindow


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H-%M-%S")

    # init global vars
    Config.initilize()


    # exit event handlers
    atexit.register(exitHandler)
    signal(SIGINT, exitHandler)

    # inireader thread
    reader = threading.Thread(
        target=InIReader.startWatchBlocking, args=(iniReaderPill,))
    threads.append(reader)
    reader.start()

    Hotkeys.registerCallback("start", startCapture)
    Hotkeys.registerCallback("stop", stopCapture)
    Hotkeys.registerCallback("lockwindow", toggleLockedWindow)
    Hotkeys.registerCallback("exit", exitHandler)
    Hotkeys.registerCallback("reset", Output.resetFishingState)

    while not mainPill.is_set():
        time.sleep(1)

        if Config.updated == True:

            Hotkeys.setupHotkeys()

            if started:
                stopCapture()
                time.sleep(1)
                startCapture()

            Config.updated = False

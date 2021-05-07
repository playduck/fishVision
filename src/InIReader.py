import logging
import configparser

import FileReload
import Config

iniPath = "config.ini"


def readini() -> None:
    logging.debug("Parsing Config")
    config = configparser.ConfigParser()
    config.read(iniPath)

    logging.debug(
        f"Sections {config.sections()} {config['HOTKEYS']}")

    Config.config = config
    Config.updated = True


def handleChanges() -> None:
    try:
        readini()
    except Exception:
        logging.debug("Error parsing ini")


def startWatchBlocking(stop_event):
    readini()
    logging.debug("Starting watching")
    FileReload.watchPathBlocking(stop_event, path=".", onUpdate=handleChanges)


if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")

    startWatchBlocking()

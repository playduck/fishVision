# https://stackoverflow.com/a/54638435/12231900

import ctypes
from ctypes import wintypes
import time
import random
import logging

import KeyCodeMap
import Config

user32 = ctypes.WinDLL("user32", use_last_error=True)
INPUT_KEYBOARD = 1
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
MAPVK_VK_TO_VSC = 0
# msdn.microsoft.com/en-us/library/dd375731
wintypes.ULONG_PTR = wintypes.WPARAM


class MOUSEINPUT(ctypes.Structure):
    _fields_ = (("dx",          wintypes.LONG),
                ("dy",          wintypes.LONG),
                ("mouseData",   wintypes.DWORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))


class KEYBDINPUT(ctypes.Structure):
    _fields_ = (("wVk",         wintypes.WORD),
                ("wScan",       wintypes.WORD),
                ("dwFlags",     wintypes.DWORD),
                ("time",        wintypes.DWORD),
                ("dwExtraInfo", wintypes.ULONG_PTR))

    def __init__(self, *args, **kwds):
        super(KEYBDINPUT, self).__init__(*args, **kwds)
        if not self.dwFlags & KEYEVENTF_UNICODE:
            self.wScan = user32.MapVirtualKeyExW(self.wVk,
                                                 MAPVK_VK_TO_VSC, 0)


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = (("uMsg",    wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD))


class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = (("ki", KEYBDINPUT),
                    ("mi", MOUSEINPUT),
                    ("hi", HARDWAREINPUT))
    _anonymous_ = ("_input",)
    _fields_ = (("type",   wintypes.DWORD),
                ("_input", _INPUT))


LPINPUT = ctypes.POINTER(INPUT)


def __randomDelay__():
    keyDuration = float(Config.config["OPTIONS"].get("keyDuration", 0.5))
    keyRandomness = ((2 * random.random()) - 1) * float(Config.config["OPTIONS"].get("keyDurationRandomnes", 0))

    sleepTime = keyDuration + keyRandomness

    time.sleep(sleepTime)


def pressKey(hexKeyCode: int):
    #logging.debug(f"Keydown {hexKeyCode}")
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def releaseKey(hexKeyCode: int):
    #logging.debug(f"Keyup {hexKeyCode}")
    x = INPUT(type=INPUT_KEYBOARD,
              ki=KEYBDINPUT(wVk=hexKeyCode, dwFlags=KEYEVENTF_KEYUP))
    user32.SendInput(1, ctypes.byref(x), ctypes.sizeof(x))


def keyByHex(hexKeyCode: int):
    pressKey(hexKeyCode)
    __randomDelay__()
    releaseKey(hexKeyCode)


def keyByName(name: str):
    keyByHex(KeyCodeMap.toKeyCode(name.lower()))


def keyCombination(combo: str):
    keys = combo.split("+")
    keys = [KeyCodeMap.toKeyCode(key) for key in keys]

    for key in keys:
        pressKey(key)

    __randomDelay__()

    for key in keys:
        releaseKey(key)

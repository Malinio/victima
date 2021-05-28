import socket
import pickle
import numpy as np

from mss import mss


def main():
    while True:
        sct = mss()
        bounding_box = {'top': 0, 'left': 0, 'width': 1920, 'height': 1080}
        sct_img = sct.grab(bounding_box)

        sock = socket.socket()
        sock.connect(('localhost', 9090))

        data_to_send = pickle.dumps(np.array(sct_img))
        sock.send(data_to_send)


if __name__ == '__main__':
    main()

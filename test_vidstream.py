from vidstream import CameraClient
from vidstream import VideoClient
from vidstream import ScreenShareClient
from PIL import Image

screen_share_client = ScreenShareClient('192.168.0.139', 9090)

screen_share_client.start_stream()

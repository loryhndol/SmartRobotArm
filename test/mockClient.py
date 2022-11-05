import sys, os

sys.path.extend([
    os.path.join(root, name) for root, dirs, _ in os.walk("../")
    for name in dirs
])

from channel.iochannel import ioChannel
from channel.endpoint import Endpoint
from utility.point3d import Point3d


class MockClient():
    ch = ioChannel()

    def __init__(self) -> None:
        # ch = ioChannel(Endpoint('192.168.31.76', 8888))

        while True:
            # img = self.ch.sync_recv()
            location_msg = self.image_processing(img)
            # self.ch.send(location_msg)

    def image_processing(img) -> Point3d:
        pass

    def get_item_center():
        pass

    def pixel2world(x: int, y: int) -> Point3d:
        pass


if __name__ == "__main__":
    cli = MockClient()

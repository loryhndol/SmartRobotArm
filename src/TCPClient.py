from channel.iochannel import ioChannel
from channel.endpoint import Endpoint
from utility.point3d import Point3d


class TCPClient():
    ch = ioChannel()

    def __init__(self) -> None:
        ch = ioChannel(Endpoint('192.168.31.76', 8888))
        ch.connect()

        while True:
            img = self.ch.sync_recv()
            location_msg = self.image_processing(img)
            self.ch.send(location_msg)

    def image_processing(img) -> Point3d:
        pass

    def get_item_center():
        pass

    def pixel2world(x: int, y: int) -> Point3d:
        pass

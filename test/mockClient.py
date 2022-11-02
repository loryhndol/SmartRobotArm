from channel.iochannel import ioChannel
from channel.endpoint import Endpoint


class MockClient():

    def __init__(self) -> None:
        # ch = ioChannel(Endpoint('192.168.31.76', 8888))
        # ch.connect()

        flag = '1'
        while True:
            print('send to server with value: ' + flag)
            # ch.send(flag)
            # msg = ch.sync_recv(1024)
            # print(msg)

    def get_item_center():
        pass

    def pixel2world(x, y):
        pass

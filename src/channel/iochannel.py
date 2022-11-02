import socket


class iChannel():

    def sync_recv():
        pass


class oChannel():

    def send():
        pass


class ioChannel(iChannel, oChannel):

    def __init__(self, endpoint) -> None:
        super().__init__()
        self.endpoint = endpoint

    def connect(self):
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockfd.connect((self.endpoint.ip, self.endpoint.port))

    def send(self):
        self.sockfd.send()

    def sync_recv(self):
        self.sockfd.recv()

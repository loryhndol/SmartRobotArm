import socket
from endpoint import Endpoint
import pickle


class iChannel():

    def sync_recv():
        pass


class oChannel():

    def send():
        pass


class ioChannel(iChannel, oChannel):

    def __init__(self, endpoint: Endpoint) -> None:
        super().__init__()
        self.endpoint = endpoint

    def connect(self):
        self.sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sockfd.connect((self.endpoint.ip, self.endpoint.port))

    def send(self, content):
        msg = pickle.dumps(content)
        self.sockfd.send(msg)

    def sync_recv(self):
        msg = self.sockfd.recv()
        content = pickle.loads(msg)
        return content

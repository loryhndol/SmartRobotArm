from channel import ioChannel, Endpoint
import socket
import numpy as np
from utility.point3d import Point3d


class TCPServer():
    ip = '192.168.31.76'
    port = 8888
    max_conn = 5

    def __init__(self) -> None:
        print("Server is starting")
        self.listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenfd.bind((self.ip, self.port))
        self.listenfd.listen(5)
        print("Server is listenting port {}, with max connection {}".format(
            self.port, self.max_conn))
        self.connfd, self.ip_addr = self.listenfd.accept()
        self.connfd.settimeout(50)
        self.ch = ioChannel(Endpoint(self.connfd))

    def move(self, A, B):
        dType.SetPTPCmdSync(api, 1, A.x, A.y, A.z, 0, 1)
        dType.SetPTPCmdSync(api, 1, B.x, B.y, B.z, 0, 1)

    def move_to(self, dst):
        dType.SetPTPCmdSync(api, 1, dst.x, dst.y, dst.z, 0, 1)
        return self

    def choose(self, weight):
        pass

    def release(self):
        pass

    def get_position(self):
        pass

    def strategy(self):
        pass

    def reset_position(self):
        dType.SetArmOrientation(api, 0, 1)
        dType.SetPTPCommonParamsSync(api, 30, 30)
        dType.SetPTPCmdSync(api, 1, 400, 0, 230, 0, 1)

    def action(self):
        dType.SetArmOrientation(api, 0, 1)
        dType.SetPTPCommonParamsSync(api, 30, 30)

        for _ in range(5):
            A = Point3d(81, 391, 80)
            B = Point3d(76, -391, 230)
            C = Point3d(76, -391, 80)
            D = Point3d(81, 391, 230)
            forward = self.move_to(A).move_to(B).move_to(C).move_to(D)
            backward = self.move_to(D).move_to(C).move_to(B).move_to(A)
            forward()
            backward()

    def event_loop(self):
        try:
            while True:
                #接收数据
                #recv data
                buf = self.ch.recv(1024)
                dat = buf.decode('UTF-8', 'strict')
                print('get data:' + dat)

                if dat == "1":
                    self.action(self.connfd)
                    server_array = np.array([1.3, 2.01, 3])
                    self.ch.send(server_array)
                elif dat != '0':  # 初始化位姿
                    self.reset_position()

                else:
                    print("close")
                    break
        except socket.timeout:
            print('time out')
            print("closing one connection")
        self.connfd.close()
        self.listenfd.close()

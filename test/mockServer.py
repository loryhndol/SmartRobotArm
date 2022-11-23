import sys, os

sys.path.extend([
    os.path.join(root, name) for root, dirs, _ in os.walk("../")
    for name in dirs
])

import workspace as ws
from channel.iochannel import ioChannel
from channel.endpoint import Endpoint
from utility.point3d import Point3d


class MockServer():
    ip = '192.168.0.1'
    port = 1234
    max_conn = 100
    arm_position = Point3d(0.0, 0.0, 0.0)

    def __init__(self, listenfd, connfd) -> None:
        print("Server is starting, listenfd: {}, connfd: {}".format(
            listenfd, connfd))
        self.listenfd = listenfd
        self.connfd = connfd
        self.ch = ioChannel(Endpoint(self.connfd))

    def move(self, A, B):
        print("Position change: {} -> {}".format(A, B))
        self.arm_position = A
        self.arm_position = B

    def move_to(self, dst: Point3d):
        print("-> {}".format(dst))
        self.arm_position = dst
        return self

    def choose(self, weight):
        pass

    def release(self):
        pass

    def get_position(self):
        pass

    def strategy(self, items_in_view: list[ws.Bag]) -> int:
        for id, bag in enumerate(items_in_view):
            lookahead_weight = self.total_weight + bag.weight

            if lookahead_weight < self.target:
                return id
        return -1

    def reset_position(self):
        self.arm_position = Point3d(400, 0, 230)
        print("reset position to: {}".format(self.arm_position))

    def action(self):
        for _ in range(2):
            A = Point3d(81, 391, 80)
            B = Point3d(76, -391, 230)
            C = Point3d(76, -391, 80)
            D = Point3d(81, 391, 230)
            self.move_to(A).move_to(B).move_to(C).move_to(D)
            self.move_to(D).move_to(C).move_to(B).move_to(A)

    def event_loop(self):
        while True:
            dat = input()
            print('get data:' + dat)

            if dat == "1":
                self.action()
            elif dat == '2':  # 初始化位姿
                self.reset_position()

            else:
                print("close")
                break


if __name__ == '__main__':
    serv = MockServer(10, 13)
    serv.event_loop()

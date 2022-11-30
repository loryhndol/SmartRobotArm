import sys, os

sys.path.extend([
    os.path.join(root, name) for root, dirs, _ in os.walk("../")
    for name in dirs
])

import workspace as ws
from channel.iochannel import ioChannel
from channel.endpoint import Endpoint
from utility.point3d import Point3d


def image2Bags(workspace: ws.Workspace, sensor) -> list[ws.Bag]:
    ret = []
    for row in range(workspace.partition[1]):
        for col in range(workspace.partition[0]):
            bag = workspace.peek2(row, col)
            if bag != None:
                ret.append(bag)
                sensor[bag.center] = bag.weight
    return ret


class MockServer():
    ip = '192.168.0.1'
    port = 1234
    max_conn = 100
    arm_position = Point3d(0.0, 0.0, 0.0)
    target = 800
    eps = 50
    cur_weight = 0

    def __init__(self, listenfd: int, connfd: int, repo: ws.Workspace,
                 dst: ws.Workspace, weight_sensor: dict) -> None:
        print("Server is starting, listenfd: {}, connfd: {}".format(
            listenfd, connfd))
        self.listenfd = listenfd
        self.connfd = connfd
        self.ch = ioChannel(Endpoint(self.connfd))
        self.repository = repo
        self.destination = dst
        self.weight_sensor = weight_sensor

    def move(self, A, B):
        print("Position change: {} -> {}".format(A, B))
        self.arm_position = A
        self.arm_position = B

    def move_to(self, dst: Point3d):
        print("-> {}".format(dst))
        self.arm_position = dst
        return self

    def choose(self, id):
        self.repository.bags[id].empty = True
        print("choose item {} at: {}".format(id,
                                             self.repository.bags[id].center))

    def release(self, location):
        print("release item at: {}".format(location))

    def get_position(self):
        pass

    def get_weight(self, coord) -> float:
        self.move_to(coord)
        return self.weight_sensor[coord]

    # 第一种策略，一次只返回一个id
    def strategy_single(self, items_in_view: list[ws.Bag]) -> tuple[int, bool]:
        finished = False
        ret = -1
        for item in items_in_view:
            lookahead = self.cur_weight + item.weight
            if lookahead < self.target + self.eps:
                self.cur_weight += item.weight
                if lookahead > self.target - self.eps:
                    finished = True

                ret = item.ID
                break

        return ret, finished

    # 第二种策略，一次返回一个id列表
    def strategy_list(self,
                      items_in_view: list[ws.Bag]) -> tuple[list[int], bool]:
        finished = False
        ret = []
        for item in items_in_view:
            lookahead = cur_weight + item.weight
            if lookahead < self.target + self.eps:
                cur_weight += item.weight
                ret.append(item.ID)
                if lookahead > self.target - self.eps:
                    finished = True
                    break
            else:
                break

        return ret, finished

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
        # 简单测试，已弃用
        # while True:
        #     dat = input()
        #     print('get data:' + dat)

        #     if dat == "1":
        #         self.action()
        #     elif dat == '2':  # 初始化位姿
        #         self.reset_position()

        #     else:
        #         print("close")
        #         break

        # 正式测试
        while True:
            print("current: {} target: {} eps: {}".format(
                self.cur_weight, self.target, self.eps))
            items_in_view: list[ws.Bag] = []
            items_in_view = image2Bags(self.repository, self.weight_sensor)

            # 然后服务器计算出最优选的物品选择并检测是否达到目标
            item_id, finished = self.strategy_single(items_in_view)
            if finished:
                print("finished")
                print("current: {} target: {} eps: {}".format(
                    self.cur_weight, self.target, self.eps))
                break
            if item_id != -1:
                self.choose(item_id)

                self.move_to(self.destination.center)

                # 服务器将重物放下
                self.release(self.destination.center)

                # 服务器返回出发地
                self.move_to(self.repository.center)

            else:
                print('unable to find a suitable item')
                break


if __name__ == '__main__':
    partition = (2, 2, 3)
    num_of_bags = 12
    repo = ws.Workspace(position=Point3d(0.0, 0.0, 0.0),
                        x_range=100,
                        y_range=100,
                        z_range=100,
                        partition=partition)

    repo.generate_bags(num_of_bags)

    dst = ws.Workspace(position=Point3d(22.0, 31.0, 0.0),
                       x_range=100,
                       y_range=100,
                       z_range=100,
                       partition=partition)

    mock_weight_sensor = {}

    serv = MockServer(10, 13, repo, dst, mock_weight_sensor)
    serv.event_loop()

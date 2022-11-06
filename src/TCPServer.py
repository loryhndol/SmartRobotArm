from channel.iochannel import ioChannel
from channel.endpoint import Endpoint
from utility.point3d import Point3d
import sensors
import workspace as ws
import socket
import numpy as np
from ServerOptions import ServerOptions


class TCPServer():

    def __init__(self) -> None:
        self.options = ServerOptions()
        print('Server Options:{}'.format(self.options))
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
        print("checking IO devices...")
        self.camera = sensors.Camera(self.options.io_ports['camera'])
        self.picker = sensors.Picker(self.options.io_ports['picker'])
        self.weight_sensor = sensors.WeightSensor(
            self.options.io_ports['weight_sensor'])

        self.arm_position = self.get_position()

    def move(self, A: Point3d, B: Point3d):
        dType.SetPTPCmdSync(api, 1, A.x, A.y, A.z, 0, 1)
        dType.SetPTPCmdSync(api, 1, B.x, B.y, B.z, 0, 1)

    def move_to(self, dst: Point3d):
        dType.SetPTPCmdSync(api, 1, dst.x, dst.y, dst.z, 0, 1)
        return self

    def choose(self, ID: int):
        self.picker.pick()

    def release(self):
        self.picker.unpick()

    def get_position(self):
        pass

    def strategy(self, items_in_view: list[ws.Bag]) -> int:
        for id, bag in enumerate(items_in_view):
            lookahead_weight = self.total_weight + bag.weight

            if lookahead_weight < self.target:
                return id
        return -1

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
            self.move_to(A).move_to(B).move_to(C).move_to(D)
            self.move_to(D).move_to(C).move_to(B).move_to(A)

    def feedback():
        pass

    def event_loop(self):
        """机械臂事件循环
        
        循环:
            当前位置: 出发地

              1. 通过相机确认重物位置
              2. 计算出需要抓取哪一个重物
              3. 抓取重物

            从出发地移动到目的地

            当前位置: 目的地

              1. 通过相机确认摆放位置
              2. 放下重物
              3. 计算反馈信息

            机械臂返回出发地
        
        """
        try:
            while True:
                img = self.camera.get_img()
                self.ch.send(img)
                items_in_view: list[ws.Bag] = []
                self.ch.sync_recv(items_in_view)

                item_id = self.strategy(items_in_view)
                if item_id != -1:
                    self.choose(item_id)

                    self.move_to(self.dest.center)

                    img = self.camera.get_img()
                    self.ch.send(img)
                    locations: list[Point3d] = []
                    self.ch.sync_recv(locations)

                    self.release(locations)

                    self.feedback()

                    self.move_to(self.repo.center)
                else:
                    print('unable to find a suitable item')
                    break

        except socket.timeout:
            print('time out')
            print("closing one connection")
        self.connfd.close()
        self.listenfd.close()

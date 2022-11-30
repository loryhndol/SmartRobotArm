from channel.iochannel import ioChannel
from channel.endpoint import Endpoint
from utility.point3d import Point3d
from ServerOptions import ServerOptions
import workspace as ws
import sensors

import socket


class TCPServer():

    def __init__(self) -> None:
        self.options = ServerOptions()
        print('Server Options:{}'.format(self.options))
        print("Server is starting")
        self.listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenfd.bind((self.options.ip, self.options.port))
        self.listenfd.listen(5)
        print("Server is listenting port {}, with max connection {}".format(
            self.options.port, self.options.max_conn))
        self.connfd, self.ip_addr = self.listenfd.accept()
        self.connfd.settimeout(50)
        self.ch = ioChannel(Endpoint(self.connfd))
        print("checking IO devices...")
        self.camera = sensors.Camera(self.options.io_ports['camera'],
                                     Point3d(0.0, 0.0, 0.0), 1.0, 100, 100)
        self.picker = sensors.Picker(self.options.io_ports['picker'])
        self.weight_sensor = sensors.WeightSensor(
            self.options.io_ports['weight_sensor'])

        self.arm_position = self.get_position()
        dType.SetArmOrientation(api, 0, 1)
        dType.SetPTPCommonParamsSync(api, 30, 30)

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

                # 服务器发送给客户端出发地照片
                img = self.camera.get_image()
                self.ch.send(img)

                # 客户端通过视觉算法处理照片得到物品的坐标
                # 客户端将物品的坐标发送给服务器
                items_coords: list[Point3d] = []
                self.ch.sync_recv(items_coords)

                # 服务器接收到物品的坐标之后，对每一个物品进行称重
                # 根据重量传感器的结果得到每个物品的重量
                items_in_view: list[ws.Bag] = []
                for id, coord in enumerate(items_coords):
                    w = self.get_weight(coord)
                    items_in_view.append(ws.Bag(id, w, coord))

                # 然后服务器计算出最优选的物品选择并检测是否达到目标
                item_id, finished = self.strategy_single(items_in_view)
                if finished:
                    print("finished.")
                    break
                if item_id != -1:
                    self.choose(item_id)

                    self.move_to(self.destination.center)

                    # 服务器拍照发送给客户端
                    img = self.camera.get_image()
                    self.ch.send(img)

                    # 客户端计算出目的地坐标发送给服务器
                    locations: list[Point3d] = []
                    self.ch.sync_recv(locations)

                    # 服务器将重物放下
                    self.release(locations)

                    # 服务器返回出发地
                    self.move_to(self.repository.center)

                else:
                    print('unable to find a suitable item')
                    break

        except socket.timeout:
            print('time out')
            print("closing one connection")
        self.connfd.close()
        self.listenfd.close()

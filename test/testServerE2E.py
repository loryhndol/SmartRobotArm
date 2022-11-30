# 端到端测试
# 将本文件添加到机械臂上运行
# 需要根据实际情况做一些语法调整
import socket
import pickle
import random


class Point3d():

    def __init__(self, nx: float, ny: float, nz: float) -> None:
        self.x = nx
        self.y = ny
        self.z = nz

    def __format__(self, __format_spec: str) -> str:
        return "(%f, %f, %f)" % (self.x, self.y, self.z)

    def __add__(self, rhs):
        return Point3d(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)


class ServerOptions():
    ip = '192.168.31.76'
    port = 8888
    max_conn = 5
    task = {'initial_weight': 0, 'target_weight': 200, 'tolerance': 10}
    coords = {
        'destination': Point3d(0.0, 0.0, 0.0),
        'repository': Point3d(100, 100, 100)
    }
    io_ports = {'camera': -1, 'picker': -1, 'weight_sensor': -1}

    def __format__(self, __format_spec: str) -> str:
        loc = "location: {}:{}\n".format(self.ip, self.port)
        max_conn = "max_conn: {}\n".format(self.max_conn)
        task = "task:\n"
        for k, v in self.task.items():
            task += "- {}: {}".format(k, v)
            task += "\n"
        coords = "coordinates:\n"
        for k, v in self.coords.items():
            coords += "- {}: {}".format(k, v)
            coords += "\n"
        io_ports = "IO Ports:\n"
        for k, v in self.io_ports.items():
            io_ports += "- {}: {}".format(k, v)
            io_ports += "\n"

        return loc + max_conn + coords + io_ports


class Endpoint():

    def __init__(self, ip: str, port: int) -> None:
        self.ip = ip
        self.port = port

    def __init__(self, ip_addr) -> None:
        pass

    def __init__(self, connfd) -> None:
        pass


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


class Sensor():

    def __init__(self, port) -> None:
        self.IO_port = port


class Camera(Sensor):

    def __init__(self, port, position, focal_length, width, height) -> None:
        super().__init__(port)
        self.position = position
        self.focal_len = focal_length
        self.width = width
        self.height = height

    def get_image(self):
        pass


class Picker(Sensor):

    def __init__(self, port) -> None:
        super().__init__(port)

    def pick():
        pass

    def unpick():
        pass


class WeightSensor(Sensor):

    def __init__(self, port) -> None:
        super().__init__(port)

    def get_weight():
        pass


def offset2id(x: int, y: int, z: int) -> int:
    group_id = z << 2
    item_id = group_id + x << 1 + y
    return item_id


# 按照 X, Y, Z 的顺序进行位置编码
def id2coord(id, partition, units) -> Point3d:
    warp_size = partition[0] * partition[1]
    group_id = int(id / warp_size)
    offset_x = (id - group_id * warp_size) % partition[0]
    offset_y = (id - group_id * warp_size) / partition[0]
    offset_z = group_id
    return Point3d(nx=units.x * offset_x + units.x,
                   ny=units.y * offset_y + units.y,
                   nz=units.z * offset_z + units.z)


class Bag():

    def __init__(self, id, weight=0.0, center=Point3d(0.0, 0.0, 0.0)) -> None:
        self.ID = id
        self.weight = weight
        self.center = center
        self.empty = False


class Workspace():
    center = Point3d(0.0, 0.0, 0.0)
    x_range = 0
    y_range = 0
    z_range = 0
    bags = []
    partition = (2, 2, 1)
    weight_array = [i for i in range(80, 160, 10)]
    used = []

    def __init__(self, position: Point3d, x_range: int, y_range: int,
                 z_range: int, partition) -> None:
        self.center = position
        self.x_range = x_range
        self.y_range = y_range
        self.z_range = z_range
        self.partition = partition

    def generate_bags(self, num, bags_weight=[]):

        if num < 0:
            raise Exception('Invalid number of bags: should be positive.')

        capacity = self.partition[0] * self.partition[1] * self.partition[2]
        if num > capacity:
            raise Exception(
                'Invalid number of bags: capacity: {} input: {}'.format(
                    capacity, num))

        if len(bags_weight) == 0:
            for bag_id in range(num):
                idx = random.randint(0, len(self.weight_array) - 1)
                self.bags.append(Bag(bag_id, self.weight_array[idx]))
        elif len(bags_weight) == num:
            for bag_id in range(num):
                self.bags.append(Bag(bag_id, bags_weight[bag_id]))
                self.used[bag_id] = False
        else:
            raise Exception(
                'Inconpatible length: num: {} bags_weight: {}'.format(
                    num, len(bags_weight)))

        # 确定单位长度
        x_unit = self.x_range / (self.partition[0] * 2)
        y_unit = self.y_range / (self.partition[1] * 2)
        z_unit = self.z_range / (self.partition[2] * 2)
        self.units = Point3d(x_unit, y_unit, z_unit)
        print("axis unit: {}".format(self.units))

        for bag in self.bags:
            bag.center = id2coord(bag.ID, self.partition, self.units)
            bag.center = bag.center + self.center

    def get_entry(self, x_offset, y_offset, z_offset) -> Point3d:
        return Point3d(
            nx=x_offset * self.units.x + self.units.x,
            ny=y_offset * self.units.y + self.units.y,
            nz=z_offset * self.units.z + self.units.z,
        )

    def top(self, row, col) -> Bag or None:
        for g in range(self.partition[2] - 1, 0, -1):
            warp_size = self.partition[0] * self.partition[1]
            idx = g * warp_size + row * self.partition[0] + col
            if idx >= len(self.bags):
                continue
            if self.bags[idx].empty:
                continue
            else:
                self.bags[idx].empty = True
                return self.bags[idx]
        return None

    def peek(self, row, col) -> bool:
        for g in range(self.partition[2] - 1, 0, -1):
            warp_size = self.partition[0] * self.partition[1]
            idx = g * warp_size + row * self.partition[0] + col
            if idx >= len(self.bags):
                continue
            if self.bags[idx].empty:
                continue
            else:
                return True
        return False

    def peek2(self, row, col) -> Bag or None:
        for g in range(self.partition[2] - 1, 0, -1):
            warp_size = self.partition[0] * self.partition[1]
            idx = g * warp_size + row * self.partition[0] + col
            if idx >= len(self.bags):
                continue
            if self.bags[idx].empty:
                continue
            else:
                return self.bags[idx]
        return None


class TCPServer():

    def __init__(self) -> None:
        self.options = ServerOptions()
        print('Server Options:\n{}'.format(self.options))
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
        self.camera = Camera(self.options.io_ports['camera'],
                             Point3d(0.0, 0.0, 0.0), 1.0, 100, 100)
        self.picker = Picker(self.options.io_ports['picker'])
        self.weight_sensor = WeightSensor(
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
    def strategy_single(self, items_in_view):
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
                items_coords = []
                self.ch.sync_recv(items_coords)

                # 服务器接收到物品的坐标之后，对每一个物品进行称重
                # 根据重量传感器的结果得到每个物品的重量
                items_in_view = []
                for id, coord in enumerate(items_coords):
                    w = self.get_weight(coord)
                    items_in_view.append(Bag(id, w, coord))

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
                    locations = []
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


server = TCPServer()
server.event_loop()

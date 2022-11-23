from utility.point3d import Point3d
import random


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
    bags: list[Bag] = []
    partition = (2, 2, 1)
    weight_array = [i for i in range(80, 160, 10)]
    used = list[bool]

    def __init__(self, position: Point3d, x_range: int, y_range: int,
                 z_range: int, partition: tuple[int, int, int]) -> None:
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


class Repository(Workspace):
    pass


class Destination(Workspace):
    current_weight = 0

from utility.point3d import Point3d


class Bag():
    ID = -1
    weight = 0.0
    center = Point3d(0.0, 0.0, 0.0)


class Workspace():
    center = Point3d(0.0, 0.0, 0.0)
    width = 0
    length = 0
    bags: list[Bag] = []
    partitions = 1


class Repository(Workspace):
    used = []


class Destination(Workspace):
    current_weight = 0

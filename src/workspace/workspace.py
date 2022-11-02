from utility.point3d import Point3d
from bag import Bag


class Workspace():
    center = Point3d(0.0, 0.0, 0.0)
    width = 0
    length = 0
    bags = Bag[...]
    partitions = 1
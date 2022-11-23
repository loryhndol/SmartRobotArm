class Point3d():

    def __init__(self, nx: float, ny: float, nz: float) -> None:
        self.x = nx
        self.y = ny
        self.z = nz

    def __format__(self, __format_spec: str) -> str:
        return "(%f, %f, %f)" % (self.x, self.y, self.z)

    def __add__(self, rhs):
        return Point3d(self.x + rhs.x, self.y + rhs.y, self.z + rhs.z)

import unittest
from utility.point3d import Point3d
from workspace import Workspace


class TestWorkspaceMethods(unittest.TestCase):

    def test_generate_bags(self):
        testWorkspace = Workspace(position=Point3d(0.0, 0.0, 0.0),
                                  x_range=100,
                                  y_range=100,
                                  z_range=100,
                                  partition=(2, 2, 3))

        testWorkspace.generate_bags(10, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        

if __name__ == '__main__':
    unittest.main()
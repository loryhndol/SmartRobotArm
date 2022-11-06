from utility.point3d import Point3d


class Sensor():
    IO_port = -1


class Camera(Sensor):
    camera_pos = Point3d(0.0, 0.0, 0.0)
    focal_len = 1.0
    width = 100
    height = 100

    def get_image():
        pass


class Picker(Sensor):

    def pick():
        pass

    def unpick():
        pass


class WeightSensor(Sensor):

    def get_weight():
        pass

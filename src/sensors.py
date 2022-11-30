from utility.point3d import Point3d


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

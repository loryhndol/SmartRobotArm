from utility.point3d import Point3d


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
        print("location: {}:{}".format(self.ip, self.port))
        print("max_conn: {}".format(self.max_conn))
        print("task:")
        for k, v in self.task:
            print("- {}: {}".format(k, v))
        print("coordinates:")
        for k, v in self.coords:
            print("- {}: {}".format(k, v))
        print("IO Ports:")
        for k, v in self.io_ports:
            print("- {}: {}".format(k, v))

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

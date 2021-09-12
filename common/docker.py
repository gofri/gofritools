import platform
import os

class Docker(object):
    MOUNT_DIR = '/mnt/root' 
    HOSTNAME = 'gofritools'

    def __init__(self):
        self.in_docker = self.is_in_docker()

    def is_in_docker(self):
        assertions = [
            platform.node() == self.HOSTNAME,
            os.path.ismount(self.MOUNT_DIR),
        ]
        return all(assertions)

    def outside_to_inside(self, path):
        if self.in_docker and os.path.isabs(path):
           path = self.MOUNT_DIR + path
        return path

    def inside_to_outside(self, path):
        if self.in_docker and path.startswith(self.MOUNT_DIR):
            path = path[len(self.MOUNT_DIR):]
        return path

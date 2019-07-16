#!//bin/python3
# encoding: utf-8
from L0.bash import Bash
from common.ifactory import IFactory


class ShellFactory(IFactory):
    DEFAULT_SHELL = 'bash'
    SHELLS = {
        'bash': Bash
    }

    def create(self, name=None):
        shell_t = self.get_shell(name)
        return shell_t()

    @classmethod
    def get_shell(cls, name):
        try:
            return cls.SHELLS[name]
        except KeyError:
            return cls.SHELLS[cls.DEFAULT_SHELL]

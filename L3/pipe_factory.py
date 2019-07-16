from L3.pipe import Pipe
from L3.nullpipe import NullPipe
from common.ifactory import IFactory
from common.utils import SimpleCache


class PipeFactory(IFactory):
    PIPES = {
        'pipe': Pipe,
        'null': NullPipe,
    }

    def __init__(self, input_):
        self.input = input_

    def create(self, name=None):
        name = name or 'pipe'
        pipe_t = self.get_pipe_type(name)
        return pipe_t(self.input)

    @classmethod
    def get_pipe_type(cls, name):
        return cls.PIPES[name]

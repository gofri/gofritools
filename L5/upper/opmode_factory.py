from common.ifactory import IFactory
from L5 import argparse 

from L5.interactive import InteractiveMode
from L5.batch import BatchMode

class OpModeFactory(IFactory):
    OP_MODES= {
        'interactive': InteractiveMode,
        'batch': BatchMode,
        'pipe': PipeMode,
    }

    def __init__(self, stack, cmdline=None):
        parser = argparse.make_parser()
        args = argparse.parse_args(parser, cmdline)
        mode_t = self.get_op_mode(args.mode)
        self.mode = mode_t(stack, parser, args)

    def create(self):
        return self.mode

    @classmethod
    def get_op_mode(cls, name):
        return cls.OP_MODES[name]

import sys
from common import utils
from common.ifactory import IFactory
from L4.stack import Stack

class StackFactory(IFactory):
    STACKS = {
        'stack': Stack,
    }

    def __init__(self):
        try:
            self.stack = utils.collect_bin_stdin()
        except utils.NoPipe:
            # XXX: hard-coded until future support in e.g. TREE
            name = 'stack'
            stack_t = self.get_stack_type(name)
            self.stack = stack_t()

    def create(self):
        return self.stack

    @classmethod
    def get_stack_type(cls, name):
        return cls.STACKS[name]

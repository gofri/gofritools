from L3.stack import Stack
from common.ifactory import IFactory


class StackFactory(IFactory):
    STACKS = {
        'stack': Stack,
    }

    def __init__(self, *args, **kwargs):
        # XXX: hard-coded until future support in e.g. TREE
        name = 'stack'
        stack_t = self.get_stack_type(name)
        self.stack = stack_t(*args, **kwargs)

    def create(self):
        return self.stack

    @classmethod
    def get_stack_type(cls, name):
        return cls.STACKS[name]

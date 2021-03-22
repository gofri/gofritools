from L3.common.ipipe import IPipe
from L2.common.virt_factory import VirtFactory


class Pipe(IPipe):
    ''' Straight-forward pipe: just pass from input to output.
        Just call the program in case the input is empty. '''

    def __init__(self, *args, **kwargs):
        self._vprog = None
        self._args_ns = None
        IPipe.__init__(self, *args, **kwargs)

    def run(self, args_ns):
        self._args_ns = args_ns
        shell_name = None  # TODO get from args_ns per need
        self._vprog = VirtFactory(self.input, shell_name).create(
            self._args_ns.command)

        self._vprog.run(**self._args_ns.__dict__)

        return self._vprog.output

    @property
    def output(self):
        assert self._vprog, 'cannot get output before running'
        return self._vprog.output

    def refresh(self, input_):
        assert self._vprog, 'cannot refresh before running'
        return self._vprog.refresh(input_)

    @property
    def stackable(self):
        return self._vprog.stackable

    @property
    def dirtying(self):
        return self._vprog.dirtying

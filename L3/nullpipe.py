from L3.lower.ipipe import IPipe
from L1.lower.results.iresult import IResult


class NullPipe(IPipe):
    ''' A pipe that does not care about input args and always returns an empty result. '''

    def __init__(self, *_, **__):
        IPipe.__init__(self, IResult())

    def run(self, args_ns):
        return self.output

    @property
    def output(self):
        return IResult()

    def refresh(self, input_):
        return self.output

    @property
    def stackable(self):
        return True # Irrelevant...

    @property
    def dirtying(self):
        return False

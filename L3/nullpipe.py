from L3.lower.ipipe import IPipe
from L1.lower.results.search_result import SearchRes


class NullPipe(IPipe):
    ''' A pipe that does not care about input args and always returns an empty result. '''

    def __init__(self, *_, **__):
        IPipe.__init__(self, SearchRes())

    def run(self, args_ns):
        return self.output

    @property
    def output(self):
        return SearchRes()

    def refresh(self, input_):
        return self.output

    @property
    def stackable(self):
        return True # Irrelevant...

    @property
    def dirtying(self):
        return False

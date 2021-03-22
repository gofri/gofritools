
#!/usr/bin/python3
# encoding: utf-8
from L2.common.ivirt import IVirt
from L1.grep import Grep


class VirtGrep(IVirt):
    ''' TODO add flag: double coloring when prog is part of the res'''

    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Grep, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        return self._virt_paths(kwargs)

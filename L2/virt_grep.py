
#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.grep import Grep


class VirtGrep(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Grep, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        if self.prev_output.texts:
            return self._native_grep(**kwargs)
        else:
            return self._virt_paths(kwargs)

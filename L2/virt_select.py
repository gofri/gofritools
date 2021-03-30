#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.select import Select


class VirtSelect(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Select, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        kwargs['search_res'] = self.prev_output
        self._underlying_prog.run(**kwargs)
        return self._underlying_prog.output

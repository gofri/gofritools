#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.find import Find
from L2.lower.virt_filter import VirtualFilter, Filteree


class VirtFind(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Find, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        if self.prev_output.texts:
            return VirtualFilter(self.prev_output, Filteree.PATH).filter(**kwargs)
        else:
            return self._virt_paths(kwargs)

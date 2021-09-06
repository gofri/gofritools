#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.find import Find


class VirtFind(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Find, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        if self.prev_output.paths:
            return self._native_find(**kwargs)
        else:
            return self._virt_paths(kwargs, text_match=False)

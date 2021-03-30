#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.element import Element


class VirtElement(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Element, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        kwargs['data'] = self.prev_output
        return self._underlying_prog.run(**kwargs)

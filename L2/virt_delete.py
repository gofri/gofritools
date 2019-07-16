#!/usr/bin/python3
# encoding: utf-8
from L2.ivirt import IVirt
from L1.delete import Delete
from common.argparse import FileLine

class VirtDelete(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Delete, stackable=False, dirtying=True)

    def _run_virt(self, **kwargs):
        kwargs = FileLine.L2_combine_pairs(kwargs, self.prev_output.records)
        self._underlying_prog.run(**kwargs)

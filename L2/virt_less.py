#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.less import Less
from L1.lower.argparse import FileLine

class VirtLess(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Less, stackable=False, dirtying=False)

    def _run_virt(self, **kwargs):
        kwargs = FileLine.L2_combine_pairs(kwargs, self.prev_output.records)
        self._underlying_prog.run(**kwargs)

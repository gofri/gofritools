#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.less import Less
from L1.lower.argparse import FileLine
from L1.lower.results.search_result import SearchResult

class VirtLess(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, stackable=False, dirtying=False)

    @classmethod
    def _action_map(cls, self):
        return { SearchResult: self and self.__handle_result }

    @classmethod
    def underlying_prog(cls):
        return Less

    def __handle_result(self, **kwargs):
        kwargs = FileLine.L2_combine_pairs(kwargs, self.prev_output.records)
        self._underlying_prog.run(**kwargs)

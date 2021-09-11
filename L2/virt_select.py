#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.select import Select
from L1.lower.results.search_result import SearchResult

class VirtSelect(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, stackable=True, dirtying=False)

    @classmethod
    def _action_map(cls, self):
        return { SearchResult: self and self.__handle_result }

    @classmethod
    def underlying_prog(cls):
        return Select

    def __handle_result(self, **kwargs):
        kwargs['search_res'] = self.prev_output
        self._underlying_prog.run(**kwargs)
        return self._underlying_prog.output

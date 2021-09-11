#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.element import Element
from L1.lower.results.search_result import SearchResult

class VirtElement(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Element, stackable=True, dirtying=False)

    @property
    def action_map(self):
        return { SearchResult: self.__handle_result }

    def __handle_result(self, **kwargs):
        kwargs['data'] = self.prev_output
        return self._underlying_prog.run(**kwargs)

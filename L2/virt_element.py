#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.element import Element
from L1.lower.results.search_result import SearchResult

class VirtElement(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, stackable=True, dirtying=False)

    @classmethod
    def _action_map(cls, self):
        return { SearchResult: self and self.__handle_result }

    @classmethod
    def underlying_prog(cls):
        return Element

    def __handle_result(self, **kwargs):
        kwargs['data'] = self.prev_output
        return self._underlying_prog.run(**kwargs)

#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.difftool import Difftool
from L1.lower.results.search_result import SearchResult

class VirtDifftool(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Difftool, stackable=False, dirtying=True)

    @property
    def action_map(self):
        return { SearchResult: self.__handle_result }

    def __handle_result(self, **kwargs):
        kwargs['files'] = self.prev_output.paths
        return self._underlying_prog.run(**kwargs)

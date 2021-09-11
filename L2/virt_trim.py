#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.trim import Trim
from L1.lower.results.search_result import SearchResult

class VirtTrim(IVirt):
    ''' TODO this should become a dirtying=True util that actually trims,
             and a visually-only trim (like current behavior) should be only in visual mode.
             dirty-trim: 
             sed -i r's/^\s*\(.*\)\s*/\1/g' (replace all leading and trailing whitespaces with NOTHING)
             '''

    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Trim, stackable=True, dirtying=False)

    @property
    def action_map(self):
        return { SearchResult: self.__handle_result }

    def __handle_result(self, **kwargs):
        kwargs['search_res'] = self.prev_output
        self._underlying_prog.run(**kwargs)
        return self._underlying_prog.output

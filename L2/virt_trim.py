#!/usr/bin/python3
# encoding: utf-8
from L2.ivirt import IVirt
from L1.trim import Trim


class VirtTrim(IVirt):
    ''' TODO this should become a dirtying=True util that actually trims,
             and a visually-only trim (like current behavior) should be only in visual mode.
             dirty-trim: 
             sed -i r's/^\s*\(.*\)\s*/\1/g' (replace all leading and trailing whitespaces with NOTHING)
             '''

    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Trim, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        # XXX: need to change for search res
        kwargs['search_res'] = self.prev_output
        self._underlying_prog.run(**kwargs)
        return self._underlying_prog.output

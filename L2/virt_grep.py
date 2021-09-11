
#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L2.lower.virt_filter import VirtualFilter, Filteree
from L1.grep import Grep
from L1.lower.results.search_result import SearchResult


class VirtGrep(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Grep, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        # Handle special case: input is only a list of files, need to grep for their text
        if isinstance(self.prev_output, SearchResult) and \
            self.prev_output.paths and not self.prev_output.texts:
            return self._virt_paths(kwargs)
    
        return VirtualFilter.virt_filter(self, Filteree.TEXT, **kwargs)

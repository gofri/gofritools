
#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L2.lower.virt_filter import VirtualFilter, Filteree
from L1.grep import Grep
from L1.lower.results.search_result import SearchResult
from L1.lower.results.iresult import IResult

class VirtGrep(VirtualFilter):
    def __init__(self, *args, **kwargs):
        VirtualFilter.__init__(self, Filteree.TEXT, *args, **kwargs, stackable=True, dirtying=False)

    @classmethod
    def underlying_prog(cls):
        return Grep

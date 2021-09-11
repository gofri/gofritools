#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.find import Find
from L2.lower.virt_filter import VirtualFilter, Filteree
from L1.lower.results.search_result import SearchResult
from L1.lower.results.iresult import IResult


class VirtFind(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, _underlying_prog_t=Find, stackable=True, dirtying=False)

    def _run_virt(self, **kwargs):
        return VirtualFilter.virt_filter(self, Filteree.PATH, **kwargs)

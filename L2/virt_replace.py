#!/usr/bin/python3
# encoding: utf-8
from L2.lower.virt_file_line import VirtFileLine
from L1.replace import Replace

class VirtReplace(VirtFileLine):
    def __init__(self, *args, **kwargs):
        VirtFileLine.__init__(self, *args, **kwargs, stackable=False, dirtying=True)

    @classmethod
    def underlying_prog(cls):
        return Replace

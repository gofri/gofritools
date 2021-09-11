#!/usr/bin/python3
# encoding: utf-8
from L2.lower.ivirt import IVirt
from L1.copy import Copy
from common.stringification import Stringification
from common import utils
from L1.lower.results.search_result import SearchResult

class VirtCopy(IVirt):
    def __init__(self, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs, stackable=False, dirtying=False)

    @classmethod
    def _action_map(cls, self):
        return { SearchResult: self and self.__handle_result }

    @classmethod
    def underlying_prog(cls):
        return Copy

    def __handle_result(self, **kwargs):
        kwargs['output_type'] = kwargs['output_type'] or utils.OutputTypes.raw
        output = Stringification.stringify_by_args(self.prev_output, **kwargs)
        kwargs['text'] = output
        return self._underlying_prog.run(**kwargs)

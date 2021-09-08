#!/usr/bin/python3
# encoding: utf-8

from abc import abstractmethod
from common import utils
from common.utils import SimpleCache
from common.argparse import add_sub_parser

class IProgram(object):
    def __init__(self, ishell):
        self.ishell = ishell

    def run(self, **kwargs):
        kwargs = self.filter_prog_args(self, kwargs)
        self._output = SimpleCache(self._run_prog, lazy=False, **kwargs)
        return self._output.fetch()

    @property
    def output(self):
        return self._output.fetch()

    def refresh(self):
        ''' Naive program-level refresh: re-run with same args, result may change depending on e.g. filesystem state. '''
        return self._output.fetch(force_refresh=True)

    @abstractmethod
    def _run_prog(self, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def arg_parser(cls, parent):
        pass

    @classmethod
    def _add_command_parser(cls, p, name, /, *args, aliases, **kwargs):
        return add_sub_parser(p, {'command':name}, *args, aliases=aliases, **kwargs)

    @classmethod
    def filter_prog_args(cls, prog, kwargs):
        res = {k: v for k, v in kwargs.items() if k in prog.params()}
        return res

    def params(self):
        return utils.get_func_args(self._run_prog)

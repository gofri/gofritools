#!/usr/bin/python3
# encoding: utf-8

from L1.lower.iprogram import IProgram
from L1.lower.results.iresult import IResult
from abc import abstractmethod
from common import utils
from common.utils import SimpleCache
import copy

class IVirt(IProgram):
    def __init__(self, ishell, prev_output, stackable=True, dirtying=True):
        ''' underlying_prog_t by implementor
            ghost = do not appear in stack
            '''

        IProgram.__init__(self, ishell)
        self.prev_output = prev_output
        self._underlying_prog = self.underlying_prog()(ishell)
        self.stackable = stackable
        self.dirtying = dirtying

    @classmethod
    def arg_parser(cls, input_data, *args, **kwargs):
        input_data = input_data or IResult()
        if cls.can_handle(input_data):
            return cls.underlying_prog().arg_parser(*args, **kwargs)

    def _run_virt_prog(self):
        retval = self._run_virt(**self.kwargs)
        if self.stackable:
            return retval
        else:
            return self.prev_output

    def run(self, **kwargs):
        self.kwargs = kwargs
        self._output = SimpleCache(self._run_virt_prog)

    def params(self):
        return utils.get_func_args(self.prog._run_virt)

    def refresh(self, prev_output):
        self.prev_output = copy.deepcopy(prev_output)
        self.run(**self.kwargs)
        return self.output

    @classmethod
    def __find_action_key(cls, input_data):
        for input_type in cls.get_action_keys():
            if isinstance(input_data, input_type):
                return input_type
        return None

    def __find_action(self, input_data):
        key = self.__find_action_key(input_data)
        return key and self.action_map[key]

    @classmethod
    def can_handle(cls, input_data):
        return cls.__find_action_key(input_data) is not None

    ''' Hack to make the keys class-level, while having the action self-self.
        see _action_map for each subclass. ''' 
    @property
    def action_map(self):
        return self._action_map(self)
    @classmethod
    def get_action_keys(cls):
        # sort by reverse-mro: loop for more-specific definition first
        return sorted(cls._action_map(None).keys(), key=lambda cls:len(cls.mro()), reverse=True)
        
    def _run_virt(self, **kwargs):
        action = self.__find_action(self.prev_output)
        if action:
            return action(**kwargs)
        else:
            raise NotImplementedError()

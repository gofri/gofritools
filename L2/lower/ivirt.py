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

    def _virt_paths(self, kwargs, text_match=True):
        '''
            Cases (path/text) of previous result:
            1) DEFAULT: w/o paths w/o text: only take new search.
            2) w/ paths w|w/o text: use paths as input for search, take path+text from result. original text has no practical effect.
            3) w/o paths w text: NOT SUPPORTED: text search is not supported anymore - we need path for searching.
        '''
        if self.prev_output.is_empty(): # #1
            return self._underlying_prog.run(**kwargs)
        else:
            kwargs['text'] = self.prev_output.texts
            kwargs['lines'] = self.prev_output.lines
            kwargs['files'] = self.prev_output.paths
            kwargs['text_colored'] = self.prev_output.texts_colored
            self._underlying_prog.run(**kwargs)
            return self._underlying_prog.output 

        prev_files = self.prev_output.paths

        # limit the search in advance to reduce run time:
        if prev_files and kwargs['files']:
            kwargs['files'] = list(set([f for f in kwargs['files'] if f in prev_files]))
        else:
            kwargs['files'] = prev_files

        lines = self.prev_output.lines

        # Run new prog
        self._underlying_prog.run(lines=lines, **kwargs)
        new_output = self._underlying_prog.output

        # Now we need a different solution for #1 vs #2:
        # #1: Take the previous output and just reduce it (XXX: keeps older highlighting)
        # #2: Just take the new output (paths+text) -- the old paths affected the search, and there is no old text.
        has_old_text = len(set(t for t in self.prev_output.texts if t.strip()))
        if has_old_text:
            output = copy.deepcopy(self.prev_output)
            output.filter_by_element('path', new_output.paths)
            if text_match:
                    output.filter_by_element('text', set(new_output.texts))
        else:
            output = new_output

        return output

# XXX: move to an independent file
from L1.lower.results.iresult import IFileLinable
class VirtFileLine(IVirt):
    @classmethod
    def _action_map(cls, self):
        return { IFileLinable: self and self._handle_result }

    def _handle_result(self, pairs, **kwargs):
        pairs += self.prev_output.as_file_line_list()
        self._underlying_prog.run(pairs=pairs, **kwargs)

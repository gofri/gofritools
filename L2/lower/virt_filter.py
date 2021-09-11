#!/usr/bin/python3
# encoding: utf-8
import re
import os

from common import utils
from L1.lower.results.search_result import SearchResult
from L1.lower.results.iresult import IResult
from L2.lower.ivirt import IVirt
from common import ui_tools
from enum import Enum, auto
import pathlib
import copy

from L1.find import join_suffix

class BasicFilter(object):
    def __init__(self, pattern, wildness, case_sensitive, whole_word, invert, **ignorable):
        self.pattern = pattern
        self.wildness = wildness
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        self.invert = invert
        self.compiled = self.compile(self.pattern)

    def match(self, *args, **kwargs):
        raise NotImplementedError()

    def post_did_match(self, *args, **kwargs):
        pass

    @classmethod
    def default_pattern(cls, pattern):
        return pattern # empty == none

    def compile(self, pattern):
        return utils.compile_re(pattern, wildness=self.wildness, case_sensitive=self.case_sensitive, whole_word=self.whole_word)

class PathFilter(BasicFilter):
    def __init__(self, pattern, /, *args, suffix, invert_suffix, **kwargs):
        BasicFilter.__init__(self, pattern, *args, **kwargs)
        self.suffix = suffix
        self.invert_suffix = invert_suffix
    
    def match(self, data):
        parts = pathlib.Path(data).parts
        path, basename = parts[:-1], parts[-1]
        filename, filext = os.path.splitext(basename)
        suffix_compiled = re.compile(join_suffix(self.suffix))

        searches = [filename]
        if self.wildness >= 1:
            searches += parts[:-1] # filename + all dir directives 

        parts_valid = any(self.compiled.search(p) for p in searches)
        suffix_valid = suffix_compiled.match(filext)
        # print(f'"{data}" for ({self.compiled.pattern},{suffix_compiled.pattern}): {parts_valid, suffix_valid}')

        return bool(parts_valid) != self.invert and bool(suffix_valid) != self.invert_suffix

    @classmethod
    def default_pattern(cls, pattern):
        return pattern or ['[^\.]*']

class TextFilter(BasicFilter):
    def match(self, data):
        return bool(self.compiled.search(data)) != self.invert

    def post_did_match(self, index, data, virt_filter):
        ''' mark the text '''
        src_line = virt_filter.text_colored_or_text(index)
        dst = virt_filter.text_colored
        matches = self.compiled.finditer(src_line)
        # print(f'try replace {self.compiled.pattern} in {src_line}')
        for m in reversed(list(matches)):
            text = m.group()
            with_color = ui_tools.colored(text, key='text')
            start, end = m.span()
            colored_match = self.compiled.sub(with_color, src_line[start:end])            
            dst[index] = src_line[:start] + colored_match + src_line[end:] 
            # print(f'replaced {text}=>{with_color} in {src_line} to get {dst[index]}')

    @classmethod
    def default_pattern(cls, pattern):
        return pattern or ['.*']
###

class Filteree(Enum):
    TEXT = auto()
    PATH = auto()
    
    def get_relevant_filteree(self, text, paths):
        options = {self.TEXT:text, self.PATH:paths}
        return options[self]
    
    def get_filter(self, *args, **kwargs):
        filter_type = self.get_filter_type()
        return filter_type(*args, **kwargs)

    def get_filter_type(self):
        options = {self.TEXT:TextFilter, self.PATH:PathFilter}
        return options[self]

    
###

class VirtualFilter(IVirt):
    def __init__(self, filteree: Filteree, *args, **kwargs):
        IVirt.__init__(self, *args, **kwargs)
        self.filteree = filteree

    def text_colored_or_text(self, index):
        if self.text_colored[index]:
            return self.text_colored[index]
        else:
            return self.text[index]

    def __prepare_filtering(self):
        print(f'prev output: {self.prev_output}')
        self.text = self.prev_output.texts
        self.text_colored = list(self.prev_output.texts_colored) # clone for local modification 
        self.paths = self.prev_output.paths
        self.lines = self.prev_output.lines

        if self.filteree == Filteree.TEXT and not any(self.text):
            new_text = []
            new_lines = []
            new_paths = []
            assert not any(self.lines), 'lines without text?'
            for i, path in enumerate(self.paths):
                with open(path) as f:
                    for i, l in enumerate(f.read().splitlines()):
                        new_paths.append(path)
                        new_text.append(l)
                        new_lines.append(i+1)
            new_colored = [''] * len(new_text)
            self.text = new_text
            self.lines = new_lines
            self.text_colored = new_colored
            self.paths = new_paths

    def filter(self, pattern, **ignorable):
        if pattern == []:
            return copy.deepcopy(self.prev_output)

        res = SearchResult()

        self.__prepare_filtering()
        pattern = self.filteree.get_filter_type().default_pattern(pattern)
        filteree = self.filteree.get_relevant_filteree(text=self.text, paths=self.paths)
        for i, t in enumerate(filteree):
            any_pattern = False
            for p in pattern:
                _filter = self.filteree.get_filter(p, **ignorable)
                if _filter.match(t):
                    any_pattern = True
                    _filter.post_did_match(i, t, self)
            if any_pattern:
                res.add_record(path=self.paths[i], line=self.lines[i], text=self.text[i], text_colored=self.text_colored[i])

        return res 

    @classmethod
    def _action_map(cls, self):
        return {
            SearchResult: self and self.filter,
            IResult: self and self._underlying_prog.run
        }

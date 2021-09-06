#!/usr/bin/python3
# encoding: utf-8
from common import utils
from common.res import SearchRes
from common import ui_tools
from enum import Enum, auto

import os

class BasicFilter(object):
    def __init__(self, pattern, wildness, case_sensitive, whole_word, invert, **ignorable):
        self.pattern = pattern
        self.wildness = wildness
        self.case_sensitive = case_sensitive
        self.whole_word = whole_word
        self.invert = invert
        self.compiled = utils.compile_re(pattern, wildness=wildness, case_sensitive=case_sensitive, whole_word=whole_word)

    def match(self, *args, **kwargs):
        raise NotImplementedError()

    def post_did_match(self, *args, **kwargs):
        pass

class PathFilter(BasicFilter):
    def __init__(self, /, *args, suffix, **kwargs):
        BasicFilter.__init__(self, *args, **kwargs)
        self.suffix = suffix
    
    def match(self, data):
        parts = data.split('/') # XXX: broken for slash in file name 
        path, basename = parts[:-1], parts[-1]
        filename, fileext = os.path.splitext(basename)

        # TODO implement find.py rules 
        
        return bool(self.compiled.search(data)) != self.invert

class TextFilter(BasicFilter):
    def match(self, data):
        return bool(self.compiled.search(data)) != self.invert

    def post_did_match(self, index, data, virt_filter):
        # TODO bug: might turn letter from capital to non or vice versa when used with -i
        #           harder than one would think... need to:
        #           1. clone the org text_colored
        #           2. finditer(data)
        #           3. for each iter:
        #               colored = sub(clone[till_this_part:])
        #               clone = clone[:till this part] + colored
        #           4. text_colored[i] = clone
        pattern_colored = ui_tools.colored(self.pattern, key='text')
        virt_filter.text_colored[index] = self.compiled.sub(pattern_colored, virt_filter.text_colored[index])

###

class Filteree(Enum):
    TEXT = auto()
    PATH = auto()
    
    def get_relevant_filteree(self, text, paths):
        options = {self.TEXT:text, self.PATH:paths}
        return options[self]
    
    def get_filter(self, *args, **kwargs):
        options = {self.TEXT:TextFilter, self.PATH:PathFilter}
        return options[self](*args, **kwargs)
    
###

class VirtualFilter(object):
    def __init__(self, prev_output, filteree: Filteree):
        self.prev_output = prev_output
        self.text = self.prev_output.texts
        self.text_colored = list(self.prev_output.texts_colored) # clone for local modification 
        self.paths = self.prev_output.paths
        self.lines = self.prev_output.lines
        self.filteree = filteree

    def filter(self, pattern, wildness, case_sensitive, whole_word, invert, **ignorable):
        res = SearchRes()
        filteree = self.filteree.get_relevant_filteree(text=self.text, paths=self.paths)
        for i, t in enumerate(filteree):
            any_pattern = False
            for p in pattern:
                _filter = self.filteree.get_filter(p, wildness, case_sensitive, whole_word, invert, **ignorable)
                if _filter.match(t):
                    any_pattern = True
                    _filter.post_did_match(i, t, self)
            if any_pattern:
                res.add_record(path=self.paths[i], line=self.lines[i], text=self.text[i], text_colored=self.text_colored[i])

        return res 

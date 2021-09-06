#!/usr/bin/python3
# encoding: utf-8
from common import utils
from common.res import SearchRes
from common import ui_tools
from enum import Enum, auto

class Filteree(Enum):
    TEXT = auto()
    PATH = auto()

    def get_relevant_filteree(self, text, paths):
        options = {self.TEXT:text, self.PATH:paths}
        return options[self]

class VirtualFilter(object):
    def __init__(self, prev_output, filteree: Filteree):
        self.prev_output = prev_output
        self.text = self.prev_output.texts
        self.text_colored = list(self.prev_output.texts_colored) # clone for local modification 
        self.paths = self.prev_output.paths
        self.lines = self.prev_output.lines
        self.filtereeType = filteree
        self.filteree = filteree.get_relevant_filteree(text=self.text, paths=self.paths)

    def filter(self, pattern, wildness, case_sensitive, whole_word, invert, **ignorable):
        res = SearchRes()

        for i, t in enumerate(self.filteree):
            any_pattern = False
            for p in pattern:
                compiled = utils.compile_re(p, wildness=wildness, case_sensitive=case_sensitive, whole_word=whole_word)
                if bool(compiled.search(t)) != invert:
                    any_pattern = True
                    if self.filtereeType == Filteree.TEXT:
                        pattern_colored = ui_tools.colored(p, key='text')
                        self.text_colored[i] = compiled.sub(pattern_colored, self.text_colored[i])
            if any_pattern:
                res.add_record(path=self.paths[i], line=self.lines[i], text=self.text[i], text_colored=self.text_colored[i])

        return res 

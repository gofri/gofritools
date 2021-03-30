#!/usr/bin/python3
# encoding: utf-8
import copy
from abc import abstractmethod


class IPipe(object):
    def __init__(self, input_):
        self.input = copy.deepcopy(input_)

    @abstractmethod
    def run(self, args_ns):
        pass

    @abstractmethod
    def refresh(self, input_):
        pass

    @property
    @abstractmethod
    def output(self):
        pass

    @property
    @abstractmethod
    def stackable(self):
        pass

    @property
    @abstractmethod
    def dirtying(self):
        pass

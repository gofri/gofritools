#!/usr/bin/python3
# encoding: utf-8
import copy
from abc import abstractmethod


class IStack(object):
    @abstractmethod
    def put(self, args_ns):
        pass

    @abstractmethod
    def cur(self):
        pass

    @abstractmethod
    def size(self):
        pass

    # fake abstract methods:
    # IStack should implement it, but it's all called from put
    @abstractmethod
    def _step_forward(self):
        pass

    @abstractmethod
    def _step_back(self):
        pass

    @abstractmethod
    def _refresh(self):
        pass

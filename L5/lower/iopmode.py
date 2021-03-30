#!/usr/bin/python3
# encoding: utf-8
import copy
from abc import abstractmethod

class IOpMode(object):
    @abstractmethod
    def run(self):
        pass
    

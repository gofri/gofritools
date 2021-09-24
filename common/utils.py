#!/usr/bin/python3
# encoding: utf-8

import sys
import json
import os
import importlib
import inspect
import pickle
import re
from enum import Enum, auto
from common import logging

class SimpleCache(object):
    class NO_DATA(object):
        pass

    def __init__(self, action, /, *args, lazy=True, **kwargs):
        self.action = action
        self.args = args
        self.kwargs = kwargs
        self.lazy = lazy
        self.data = self.NO_DATA
        if not self.lazy:
            self.fetch()

    def fetch(self, force_refresh=False):
        if self.data == self.NO_DATA or force_refresh:
            self.data = self.action(*self.args, **self.kwargs)
        return self.data

def get_wild_version(pattern, wildness):
    def replace_separators(x): return x.replace(
        '-', '_').replace(' ', '_').replace('_', '[ _-]+')
    if wildness == 0:
        return pattern
    elif wildness >= 1:
        return replace_separators(pattern)

class MultipleFiles(object):
    @staticmethod
    def get_multiple_names(names):
        if isinstance(names, str):
            return [names]
        elif isinstance(names, list) or isinstance(names, map):
            return names
        else:
            raise TypeError()

    def __init__(self, filenames, mode="r+", ignore_dirs=True):
        self.filenames = MultipleFiles.get_multiple_names(filenames)
        self.mode = mode
        self.ignore_dirs = ignore_dirs

        self.of = []

    def __enter__(self):
        for f in self.filenames:
            try:
                self.of += [open(f, self.mode)]
            except IsADirectoryError:
                if not self.ignore_dirs:
                    raise

        return self.of

    def __exit__(self, _, __, ___):
        for f in self.of:
            try:
                f.close()
            except:
                pass
        self.of = []


class ignore_failure(object):
    def __init__(self, log_exception=False):
        self.log_exception = log_exception

    def __enter__(self):
        pass

    def __exit__(self, ex_type, __, ___):
        from . import logging
        if self.log_exception:
            logging.log_ex()
        # Do not throw outside the "with" clause, unless it is Ctrl-C
        return ex_type != KeyboardInterrupt


def jsonize(data):
    return json.dumps(data, indent=4, default=lambda self: self.__dict__)

def dejsonize(json_str):
    return json.loads(json_str)


def picklize(data):
    return pickle.dumps(data)


def depicklize(pkl_str):
    return pickle.loads(pkl_str)


def depicklize_file(f):
    return pickle.load(f)


def unify_paths(paths):
    unique_paths = []

    fullpaths = set([os.path.abspath(p) for p in paths])

    for p in paths:
        fullp = os.path.abspath(p)
        if fullp in fullpaths:
            unique_paths.append(p)
            fullpaths.remove(fullp)

    return unique_paths


def get_func(module, func):
    try:
        mod = importlib.import_module('.'.join([__package__, module]))
        return getattr(mod, func)
    except:
        return None


def get_func_args(func):
    return inspect.getfullargspec(func).args


def get_ignore_list(ignore_file=None):
    DEFAULT_IGNORE_FILE = '.gofignore'
    ignore_file = ignore_file or DEFAULT_IGNORE_FILE
    with open(ignore_file, 'r') as f:
        return f.read().splitlines()

def should_ignore_record(record):
    ''' returns ignored path if should be ignored, None otherwise. '''
    ignore_list = get_ignore_list()
    for path in ignore_list:
        if record.path.startswith(path):
            return path

    return None


def in_kwargs(keys, kwargs):
    if isinstance(keys, list):
        return any(in_kwargs(k, kwargs) for k in keys)
    else:
        return bool(kwargs.get(keys))


def n_trues(options, func=bool, n=1):
    return sum(map(func, options))


class OutputTypes(Enum):
    raw = auto()
    r = auto()
    human = auto()
    h = auto()
    json = auto()
    j = auto()

    @classmethod
    def make(cls, type_str, default=None):
        for e in cls:
            if type_str == e.name:
                return e

        if default and default in cls:
            return default

        raise KeyError(type_str)

    @classmethod
    def options(cls):
        return [e.name for e in cls]

    @classmethod
    def make_choice(cls, choice, r=None, h=None, j=None, default=None):
        ''' According to choice, return the value corresponding r/h/j '''
        choice = (isinstance(choice, cls)
                  and choice) or cls.make(choice, default)
        if choice in (cls.r, cls.raw):
            return r
        elif choice in (cls.h, cls.human):
            return h
        elif choice in (cls.j, cls.json):
            return j
        else:
            raise KeyError(choice)

def is_pipe(fp):
    return not fp.isatty()

class NoPipe(Exception): pass
def collect_bin_stdin():
    if not is_pipe(sys.stdin):
        raise NoPipe()

    return depicklize_file(sys.stdin.buffer)

def compile_re(pattern, case_sensitive=False, wildness=0, whole_word=False):
    pattern = rf'\b{pattern}\b' if whole_word else pattern
    pattern = get_wild_version(pattern, wildness)
    flags = 0 if case_sensitive else re.IGNORECASE
    return re.compile(pattern, flags)

def safe_splitlines(text):
    pure_linebreak = re.compile(r'\u000a')
    res = pure_linebreak.split(text)
    if res and not res[-1]:
        res = res[:-1]
    return res

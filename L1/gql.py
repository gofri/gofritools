#!/usr/bin/python3
# encoding: utf-8

import enum
from L1.lower.results.search_result import SearchRes
from L1.lower.argparse import common_pattern_parser_partial
from enum import Enum, auto
from L1.lower.iprogram import IProgram
import re as pyre

# --- 

class ObjField(object):
    ''' A general purpose field-of-object association. '''
    def __init__(self, obj, key):
        self.obj = obj
        self.key = key
    
    def get(self):
        return self.obj.get(self.key)

    def __getattr__(self, attr):
        return getattr(self.get(), attr)

    def __contains__(self, key):
        return key in self.get()

class ReWrap(object):
    ''' A wrap around regular-expression module for a given string. '''
    def __init__(self, string):
        self.string = string
    
    def __getattr__(self, attr):
        func = getattr(pyre, attr)
        return lambda *args, **kwargs: func(*args, **kwargs, string=self.string)

class StrField(ObjField):
    ''' A string wrapper. '''
    def __init__(self, *args, **kwargs):
        ObjField.__init__(self, *args, **kwargs)
        self.re = ReWrap(self.get())

class GqlRecordTester(object):
    def __init__(self, query):
        self.query = query
        self.tester = eval('lambda path,text,line: ' + self.query)

    def test(self, record):
        path = StrField(record, 'path')
        text = StrField(record, 'text')
        line = ObjField(record, 'line')
        return self.tester(path, text, line)

# ---

class GQL(IProgram):
    ''' gofri query language. '''
    def _run_prog(self, data, query):
        tester = GqlRecordTester(query)
        new_data = list(filter(tester.test, data.records))
        return SearchRes(records=new_data)

    # XXX: implement prompt-for-empty-query on virt_ level    
    @classmethod
    def arg_parser(cls, parent):
        gql_parser = cls._add_command_parser(parent, 'gql', aliases=['x'], parents=[], help='Gofri query language - a simple pythonic query language (read the doc)')
        gql_parser.add_argument('--query', help='the gql query', default=None)

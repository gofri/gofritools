#!/usr/bin/python3
import argparse

class FileLine(object):
    SEPARATOR = ':'

    def __init__(self, file_, line=''):
        file_ = file_.strip()
        line = str(line).strip()
        if not file_:
            raise argparse.ArgumentError((file_, line), "invalid missing file")
        if line and int(line) < 0:
            raise argparse.ArgumentError(line, "Invalid line")

        self.file = file_
        self.line = line

    @staticmethod
    def order_key(fl):
        try:
            line = int(fl.line)
        except Exception:
            line = -1 # no-line implies whole-file, so set it first
        return (fl.file, line)

    @classmethod
    def from_str(cls, fileline):
        return cls.from_tuple(fileline.split(cls.SEPARATOR))

    @classmethod
    def from_tuple(cls, tup):
        return FileLine(*tup)

    @classmethod
    def as_safe_list(cls, fl_list, sorted_=True, unique=True, reverse=True):
        '''
            Safe list of file-line.
                Sorted: a consistent order.
                Unique: avoid duplicate actions.
                Reverse: when deleting lines, avoid the need to take deleted lines into account.
        '''
        if unique:
            fl_list = {cls.order_key(fl):fl for fl in fl_list}.values()
        if sorted_:
            fl_list = sorted(fl_list, key=cls.order_key, reverse=reverse)

        return fl_list

    @classmethod
    def L2_combine_pairs(cls, kwargs, records):
        KEY = 'pairs'
        pairs = kwargs[KEY] or []
        pairs += [cls(r.path, r.line) for r in records]
        kwargs[KEY] = pairs
        return kwargs

    def __str__(self):
        return f'{self.file}:{self.line}'
    
    def __repr__(self):
        return str(self)

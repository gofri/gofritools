#!/usr/bin/python3
import argparse

from common import utils

def ExtraFlag(flag):
    flag = flag.strip()

    if len(flag) == 0:
        return None

    if len(flag) == 1:  # Signle char
        prefix = '-'
    elif flag[1] == '=':  # Single char with value
        prefix = '-'
        flag = flag[:1] + flag[2:]
    else:  # Multiple chars (with and w/o value)
        prefix = '--'

    flag = prefix + flag

    return flag

def general_purpose_parser():
    # General Purpose Flags
    general_purpose = argparse.ArgumentParser(add_help=False)
    general_purpose.add_argument(
        '-v', '--verbosity', action='count', help='set verbosity level', default=0)
    general_purpose.add_argument(
        '-V', '--no-verbosity', action='count', help='decrease verbosity level', default=0)
    general_purpose.add_argument(
        '-X', '--extra-flags', help='Append extra flags (overrides other flags. -/-- is added automatically)', type=ExtraFlag, nargs='+', default=[])
    general_purpose.add_argument(
        '--gof-ignore', help='Provide file which contains string literals that must not appear in any path in result', type=argparse.FileType('r'), default=None)
    general_purpose.add_argument('-o', '--output-type', help='Data format for the output',
                                 type=str, choices=utils.OutputTypes.options(), default=None)

    return general_purpose 


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

def add_sub_parser(p, kv_dict, /, *args, aliases, **kwargs):
    ''' kv_dict = arg name to set instead of alias '''
    assert len(kv_dict) == 1, "expecting NAME=name, e.g. command=grep."
    name = kv_dict.values() # parser name
    res = p.add_parser(*name, *args, aliases=aliases, **kwargs)
    res.set_defaults(**kv_dict)
    return res

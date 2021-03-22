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


def add_sub_parser(p, kv_dict, /, *args, aliases, **kwargs):
    ''' kv_dict = arg name to set instead of alias '''
    assert len(kv_dict) == 1, "expecting NAME=name, e.g. command=grep."
    name = kv_dict.values() # parser name
    res = p.add_parser(*name, *args, aliases=aliases, **kwargs)
    res.set_defaults(**kv_dict)
    return res

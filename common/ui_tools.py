#!/usr/bin/python3
# encoding: utf-8

import math
import colorama
import re
from L0.bash import Bash


def uncolor(text):
    return Bash().run_cmd(['ansi2txt'], stdin=text)['stdout']


def get_clear_screen_str():
    return colorama.ansi.clear_screen()


def clear_screen():
    print(get_clear_screen_str())


def colored(text, color='', bg='', key=None, end=True):
    def get_color(c, bundle):
        return bundle.__dict__[c.upper()] if c else ''

    if key is not None:
        newcolor, newbg = color_by_key(key)
        color = color or newcolor or 'white'
        bg = bg or newbg

    colored = get_color(color, colorama.Fore) + \
        get_color(bg, colorama.Back) + \
        str(text)
    if end:
        colored = end_of_color(colored)

    return colored


def end_of_color(text):
    return text + colorama.Style.RESET_ALL


def get_num_width(num):
    return int(math.ceil(math.log10(num)))


def get_index_width(lst):
    return get_num_width(len(lst))


def style_index(index, width, is_colored=True):
    text = str(index).rjust(width) + ')'
    if is_colored:
        text = colored(text, key='index')
    return text

# Interactive List


def get_as_incrementing_list(lst, formatter=None, is_colored=False, **kwargs):
    if not lst:
        return ''

    if formatter is None:
        def formatter(x, _): return str(x)

    width = get_index_width(lst)

    res = []
    prefix = ''
    actual_prefix = ''
    for i, v in enumerate(lst):
        index = style_index(i, width, is_colored)
        v, new_prefix, break_before = formatter(
            i, v, prev_context=prefix, **kwargs)
        if prefix == new_prefix:
            new_prefix = break_before = ''

        # Add small indentation
        if prefix or new_prefix:
            actual_prefix = new_prefix + ' '*3

        row = f'{break_before}{actual_prefix}{index} {v}'
        prefix = new_prefix or prefix
        res += [row]

    return '\n'.join(res)


def color_by_key(key):
    COLORS = {
        'path': ('lightmagenta_ex', ''),
        'line': ('green', ''),
        'text': ('red', ''),
        'index': ('', 'black'),
        'separator': ('lightyellow_ex', ''),
        'caller': ('cyan', ''),
        'declaration': ('red', ''),
        'arg': ('red', ''),
        'shortflag': ('lightyellow_ex', ''),
        'flag': ('green', ''),
        'prompt': ('cyan', ''),
    }

    if key in COLORS.keys():
        return COLORS[key]

    return '', ''

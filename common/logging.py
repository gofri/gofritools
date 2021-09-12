#!/usr/bin/python3
# encoding: utf-8

import traceback
import sys
from common import ui_tools, docker

VERBOSE_NONE = 0
VERBOSE_1 = 1
VERBOSE_2 = 2
VERBOSE_3 = 3

global_verbosity = VERBOSE_NONE


def set_verbosity(verbosity):
    global global_verbosity
    global_verbosity = verbosity


def verbose_print(data, min_verbosity=VERBOSE_1):
    global global_verbosity
    if global_verbosity >= min_verbosity:
        print_to_stderr(data, color='lightblack_ex')


def verbose_print_cmd(cmd, label=''):
    d = docker.Docker()
    friendly_cmd = [d.inside_to_outside(x) for x in cmd]
    oneline = ' '.join((f"'{x}'" if i>0 else x for i, x in enumerate(friendly_cmd)))
    oneline = ui_tools.colored(oneline, bg='lightblue_ex')
    verbose_print(f'{label} Executing: {cmd} == \n{oneline}', VERBOSE_2)

def print_to_stderr(data, color='red', verbose_prefix=True):
    print(ui_tools.colored('VERBOSE | ' + str(data), color), file=sys.stderr)


def print_warning(data, color='lightred_ex', warning_prefix=True):
    def colorized(t): return ui_tools.colored(str(t), color)
    print(colorized('WARNING | ') + colorized(data), file=sys.stderr)


def log_ex():
    print_to_stderr(traceback.format_exc(), verbose_prefix=False)

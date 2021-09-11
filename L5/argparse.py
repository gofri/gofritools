import argparse
import argcomplete
from common.argparse import add_sub_parser
from common import utils
from L1.select import Select
from common.argparse import general_purpose_parser
from common.ui_tools import colored
from L1.upper.program_factory import ProgramFactory
from L2.upper.virt_factory import VirtFactory
import shlex
import readline
import argcomplete
import os

''' DEPRECATED: started moving to each prog '''
def add_sub_parser(p, kv_dict, /, *args, aliases, **kwargs):
    ''' kv_dict = arg name to set instead of alias '''
    assert len(kv_dict) == 1, "expecting NAME=name, e.g. command=grep."
    name = kv_dict.values() # parser name
    res = p.add_parser(*name, *args, aliases=aliases, **kwargs)
    res.set_defaults(**kv_dict)
    return res

def add_command_parser(p, name, /, *args, aliases, **kwargs):
    return add_sub_parser(p, {'command':name}, *args, aliases=aliases, **kwargs)
''' END OF DEPRACTED '''

def mode_parser(parser):

    def add_mode_parser(p, name, /, *args, aliases, **kwargs):
        return add_sub_parser(p, {'mode':name}, *args, aliases=aliases, **kwargs)

    subparsers = parser.add_subparsers(dest='mode', required=True)
    parsers = {}

    for p in ('interactive', 'batch', 'pipe'):
        parsers[p] = add_mode_parser(subparsers, p, aliases=[p[0]], help=f'{p.capitalize()} mode')

    return parsers

def add_commands_parser(parser, interactive, virt, required, input_data):
    # TODO move this argparsing to virt layer 
    subparsers = parser.add_subparsers(dest='command', required=virt)

    VirtFactory.arg_parser(input_data, subparsers)
    # ProgramFactory.arg_parser(subparsers)

    # INTERACTIVE-DEPENDENT
    if interactive:
        exit_parser = add_command_parser(subparsers, 
            'quit', aliases=['q'], help='Quit')
        stepb_parser = add_command_parser(subparsers, 'stepb', aliases=[
                                            '<', ','], help='Go to stepb result')
        stepf_parser = add_command_parser(subparsers, 'stepf', aliases=[
                                            '>', '.'], help='Go to stepf result')

    if required:
        subparsers.required = True

def match_to_key(match):
    if match.startswith('--'):
        return 'flag'
    elif match.startswith('-'):
        return 'shortflag'
    else:
        return 'arg'

def colorize_match(match):
    key = match_to_key(match)
    return colored(match, key=key)

def match_sort_key(match):
    return (match_to_key(match), match)

# TODO also need to make this an infra
g_prompt = '' # TODO replace functions here with staefull class instead of using global
def display_completion_func(substitution, matches, longest_match_length):
    global g_prompt
    matches = sorted([shlex.split(m)[-1] for m in matches], key=match_sort_key)
    longest = max(len(m) for m in matches)
    TAB = 4
    WIDTH = int(0.7 * os.get_terminal_size().columns)
    if longest % TAB != 0: # round up
        longest = longest + (TAB - longest%TAB) 
    longest += TAB # extra space between cells

    offset = 0
    res = ''
    prev_key = ''
    try:
        for m in matches:
            key = match_to_key(m)
            if offset + len(m) > WIDTH or key != prev_key:
                res += '\n'
                offset = 0
            res += colorize_match(m.ljust(longest))
            offset += longest
            prev_key = key

        print(res + "\n" + g_prompt + readline.get_line_buffer(), end='')
        readline.redisplay()
    except Exception as e:
        print(e)

    return res
        
def init_parsing_completion(interactive):
    if interactive:
        readline.set_completer_delims("")
        readline.parse_and_bind("tab: complete")
        readline.set_completion_display_matches_hook(display_completion_func)
        try:
            readline.read_history_file()
        except FileNotFoundError:
            pass


class FilteredFinder(argcomplete.CompletionFinder):
    def __init__(self, *args, **kwargs):
        argcomplete.CompletionFinder.__init__(self, *args, **kwargs)

    def quote_completions(self, completions, cword_prequote, last_wordbreak_pos):
        res = argcomplete.CompletionFinder.quote_completions(self, completions, cword_prequote, last_wordbreak_pos)
        # print(res) # no filtering at this time
        return res


def make_parser(interactive=False, virt=False, input_data=None):
    # Setup argument parser
    general_purpose = general_purpose_parser()
    parser = argparse.ArgumentParser(parents=[general_purpose])

    ''' Setup argument parser '''
    if interactive:
        mode_parsers = {'interactive': parser} 
    else:
        mode_parsers = mode_parser(parser)
        
    for name, p in mode_parsers.items():
        add_commands_parser(p, interactive=interactive, virt=virt, required=(name != 'interactive'), input_data=input_data)

    # Autocomplete
    argcomplete.autocomplete(parser)
    completer = FilteredFinder(parser, default_completer=None) # argcomplete.CompletionFinder(parser)
    readline.set_completer(completer.rl_complete)

    return parser

def parse_args(parser, cmdline=None):
    # Process arguments trick: use parse_known_args to enable ignoring multiple commands in a single line
    args = parser.parse_args(cmdline)

    # TODO use a standard count positive+negative
    args.verbosity -= args.no_verbosity
    del args.no_verbosity

    return args

def read_cmdline(prompt=''):
    global g_prompt
    g_prompt = colored(prompt, key='prompt') 
    res = shlex.split(input(g_prompt))
    readline.write_history_file()
    return res

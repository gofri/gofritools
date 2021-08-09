import argparse
import argcomplete
from common.argparse import add_sub_parser
from L1.lower.argparse import FileLine
from common import utils
from L1.select import Select
from common.argparse import general_purpose_parser
from L1.upper.program_factory import ProgramFactory
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

    for p in ('interactive', 'batch'):
        parsers[p] = add_mode_parser(subparsers, p, aliases=[p[0]], help=f'{p.capitalize()} mode')

    return parsers

def add_commands_parser(parser, interactive, virt, required):
    # TODO interactive/virt ==> will move naturally when each layer exports its argparse
    subparsers = parser.add_subparsers(dest='command', required=virt)

    ProgramFactory.arg_parser(subparsers)

    # INTERACTIVE-DEPENDENT
    if interactive:
        exit_parser = add_command_parser(subparsers, 
            'quit', aliases=['q'], help='Quit')
        stepb_parser = add_command_parser(subparsers, 'stepb', aliases=[
                                            '<', ','], help='Go to stepb result')
        stepf_parser = add_command_parser(subparsers, 'stepf', aliases=[
                                            '>', '.'], help='Go to stepf result')
    else:

        # Passthrough command
        passthrough_parser = add_command_parser(subparsers, 
            'passthrough', aliases=['p'], help='ignore all args and print stdin')
        passthrough_parser.add_argument('ignored-args', nargs='*')

    if required:
        subparsers.required = True

g_prompt = '' # TODO replace functions here with staefull class instead of using global
def display_completion_func(substitution, matches, longest_match_length):
    global g_prompt
    matches = sorted([shlex.split(m)[-1] for m in matches])
    longest = max(len(m) for m in matches)
    TAB = 4
    WIDTH = int(0.7 * os.get_terminal_size().columns)
    if longest % TAB != 0: # round up
        longest = longest + (TAB - longest%TAB) 
    longest += TAB # extra space between cells

    offset = 0
    res = '\n'
    try:
        for m in matches:
            if offset + len(m) > WIDTH:
                res += '\n'
                offset = 0
            res += m.ljust(longest)
            offset += longest
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


def make_parser(interactive=False, virt=False):
    # Setup argument parser
    general_purpose = general_purpose_parser()
    parser = argparse.ArgumentParser(parents=[general_purpose])

    ''' Setup argument parser '''
    if interactive:
        mode_parsers = {'interactive': parser} 
    else:
        mode_parsers = mode_parser(parser)
        
    for name, p in mode_parsers.items():
        add_commands_parser(p, interactive=interactive, virt=virt, required=(name != 'interactive'))

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
    g_prompt = prompt
    res = shlex.split(input(prompt))
    readline.write_history_file()
    return res

import argparse
import argcomplete
from common import argparse as argparseex
from common import utils

from L1.select import Select

def add_sub_parser(p, kv_dict, /, *args, aliases, **kwargs):
    ''' kv_dict = arg name to set instead of alias '''
    assert len(kv_dict) == 1, "expecting NAME=name, e.g. command=grep."
    name = kv_dict.values() # parser name
    res = p.add_parser(*name, *args, aliases=aliases, **kwargs)
    res.set_defaults(**kv_dict)
    return res

def add_command_parser(p, name, /, *args, aliases, **kwargs):
    return add_sub_parser(p, {'command':name}, *args, aliases=aliases, **kwargs)

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

def mode_parser(parser):

    def add_mode_parser(p, name, /, *args, aliases, **kwargs):
        return add_sub_parser(p, {'mode':name}, *args, aliases=aliases, **kwargs)

    subparsers = parser.add_subparsers(dest='mode')
    parsers = {}

    parsers['interactive'] = add_mode_parser(subparsers, 
        'interactive', aliases=['i'], parents=[], help='Interactive mode')
    parsers['batch'] = add_mode_parser(subparsers, 
        'batch', aliases=['b'], parents=[], help='Batch mode')

    return parsers

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

def common_pattern_parser():
    ''' Common flags for cmds with a pattern '''
    common_pattern = argparse.ArgumentParser(add_help=False)
    common_pattern.add_argument(
        'pattern', help='The pattern to test', default=['.*'], nargs='*')
    common_pattern.add_argument('-i', '--case-insensitive', dest='case_sensitive',
                                help='Case sevsitive search (insensitive by default)', action='store_false', default=True)
    common_pattern.add_argument('-@', '--wildness', help='Use incrementally wilder search (1=surround by wildcards. 2=convention variations)',
                                action='count', default=0)
    common_pattern.add_argument(
        '-f', '--files', help='Limit the operation to specific files / directories', type=str, nargs='+', default=[])

    return common_pattern

def common_file_line_parser():
    common_file_line = argparse.ArgumentParser(add_help=False)
    common_file_line.add_argument(
        'pairs', help='One or more [file]s or [file,line] pairs', type=argparseex.FileLine.from_str, nargs="?")

    return common_file_line

def add_commands_parser(parser, interactive, virt, required):
    # TODO interactive/virt ==> will move naturally when each layer exports its argparse
    subparsers = parser.add_subparsers(dest='command')

    # common
    common_pattern = common_pattern_parser()
    common_file_line = common_file_line_parser()

    # Grep-specific
    grep_parser = add_command_parser(subparsers, 'grep', aliases='g', parents=[
                                        common_pattern], help='grep operations (note: searches git repo by default)')
    grep_parser.add_argument(
        '-w', '--whole-word', help='grep for whole word', action='store_true', default=False)
    inputs = grep_parser.add_mutually_exclusive_group()
    inputs.add_argument('-g', '--git', help='Search files within the git repo',
                        action='store_true', dest='git', default=True)
    inputs.add_argument(
        '-G', '--no-git', help='Do not search within git repo', action='store_false', dest='git')
    inputs.add_argument('-t', '--untracked', help='When searching git, search untracked files',
                        action='store_true')
    inputs.add_argument(
        '--text', help='Grep text rather than files - input from this flag', type=str, default=None)
    inputs.add_argument('-p', '--context', help='Grab context for the result (works for c files)', action='store_true', dest='context', default=True)
    inputs.add_argument('-P', '--no-context', help='DO NOT grab context for the result', action='store_false', dest='context')
    grep_parser.add_argument('--exclude-files', nargs='*', type=str,
                             help='file patterns to exclude', default=['*.pdf'])  # Breaks encoding
    grep_parser.add_argument(
        '-v', '--invert', action='store_true', help='invert match (like grep -v)')

    # Find-specific
    find_parser = add_command_parser(subparsers, 'find', aliases='f', parents=[
                                        common_pattern], help='find operations')
    suffix_options = find_parser.add_mutually_exclusive_group()
    suffix_options.add_argument('-s', '--suffix', nargs='*', type=str, help='File extension (e.g. cpp, py)', default=[
                                'py', 'c', 'cpp', 'cc', 'h', 'hpp', 'java', 'md', 'jinja', 'jinja2', 'json', 'rpm', 'sh', 'text', 'txt', 'go', 'js'])
    suffix_options.add_argument(
        '-S', '--no-suffix', action='store_false', dest='suffix', help='No file extension')

    # Vim-specific
    vim_parser = add_command_parser(subparsers, 
        'vim', aliases=['v'], parents=[common_file_line], help='Open file in vim')
    vim_parser.add_argument('-v', '--view-mode', help='Choose view mode',
                            choices=['c', 'combo', 's', 'series'], default='combo')

    # Less-specific
    less_parser = add_command_parser(subparsers, 
        'less', aliases=['l'], parents=[common_file_line], help='Open file in less')

    # Replace-specific
    replace_parser = add_command_parser(subparsers, 'replace', aliases=['r'], parents=[common_file_line],
        help='replace text with other text (sed-based)')
    replace_parser.add_argument('before', help='pattern to search', type=str)
    replace_parser.add_argument(
        'after', help='pattern to set isntead', type=str)
    replace_parser.add_argument('-G', '--no-global-replace', dest='global_replace', default=True,
                                help='disable global replace (enabled by default)', action='store_false')

    # Delete-specific
    delete_parser = add_command_parser(subparsers, 
        'delete', aliases=['d'], parents=[common_file_line], help='delete the line (sed-based)')

    # Difftool-specific
    difftool_parser = add_command_parser(subparsers, 
        'difftool', aliases=['dt'], parents=[], help='Open file in difftool')
    difftool_parser.add_argument(
        'files', help='One or more files', type=str, nargs="*", default=[])
    difftool_parser.add_argument(
        '--tool', help='Choose tool to use', type=str, default='meld')

    # Copy-specific
    copy_parser = add_command_parser(subparsers, 
        'copy', aliases=['c'], parents=[], help='Copy the output')
    copy_parser.add_argument('-s', '--selection', help='copy type',
                             default='clip-board', choices=['primary', 'secondary', 'clip-board'])
    copy_parser.add_argument('-t', '--text', help='text to copy', default='')
    copy_parser.add_argument('-x', '--xargs', help='xargs (replace line-break with space)', action='store_true', default=False)


    # Trim-specific
    trim_parser = add_command_parser(subparsers, 
        'trim', aliases='t', parents=[], help='Trim text (strip)')

    # VIRT-DEPENDENT
    if virt or True: # TODO fix: batch mode with pipe should have virt=True... will probably be implemented when batch has a subparser
        # Select-specific
        select_parser = add_command_parser(subparsers, 'select', aliases='s', parents=[
        ], help='Select multiple ranges of a list by indices')
        select_parser.add_argument(
            'ranges', help='list of space separated row indices (N) or index ranges (N1-N2)', type=Select.RangeType, nargs='+')
        select_parser.add_argument(
            '--data-list', help='The list to operate on', nargs="+", default=[])

        # Element-specific
        element_parser = add_command_parser(subparsers, 'element', aliases=['e'], parents=[
        ], help='Select one or more element from previous output (path/line/text/text_colored)')
        element_parser.add_argument('elements', help='element', nargs='*')
        element_parser.add_argument(
            '-s', '--sort', help='Sort (instead of choose) the element.', action='store_true')
        element_parser.add_argument(
            '-u', '--unify', help='Unify the results based on a single element', action='store_true')
        element_parser.add_argument('-n', '--no-choice', dest='do_choice', default=True,
                                    help='Prevent choosing the element (for e.g. unify)', action='store_false')
        element_parser.add_argument('-T', '--no-trim-on-sort', dest='trim_on_sort', default=True,
                                    help='Prevent trim before sorting (trimming only for sort - does not effect search res)', action='store_false')

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
    return parser

def parse_args(parser, cmdline=None):
    # Process arguments trick: use parse_known_args to enable ignoring multiple commands in a single line
    args = parser.parse_args(cmdline)

    # TODO use a standard count positive+negative
    args.verbosity -= args.no_verbosity
    del args.no_verbosity

    return args

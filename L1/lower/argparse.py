import argparse
from common import ui_tools
from common import utils
from L1.lower.fileline import FileLine

def common_pattern_parser_partial():
    common_pattern = argparse.ArgumentParser(add_help=False)
    common_pattern.add_argument(
        'pattern', help='The pattern to test', default=None, nargs='*')
    common_pattern.add_argument('-i', '--case-insensitive', dest='case_sensitive',
                                help='Case sevsitive search (insensitive by default)', action='store_false', default=True)
    common_pattern.add_argument('-@', '--wildness', help='Use incrementally wilder search (1=surround by wildcards. 2=convention variations)',
                                action='count', default=0)
    return common_pattern

def common_pattern_parser():
    ''' Common flags for cmds with a pattern '''
    common_pattern = common_pattern_parser_partial()
    def docker_path(s):
        if s.startswith('/'):
           s = '/mnt/root' + s 
        return s

    common_pattern.add_argument(
        '-f', '--files', help='Limit the operation to specific files / directories', type=docker_path, nargs='+', default=[])
    common_pattern.add_argument(
        '-v', '--invert', action='store_true', help='invert match (like grep -v)')
    common_pattern.add_argument(
        '-w', '--whole-word', help='grep for whole word', action='store_true', default=False)

    return common_pattern

def common_file_line_parser():
    common_file_line = argparse.ArgumentParser(add_help=False)
    common_file_line.add_argument(
        'pairs', help='One or more [file]s or [file,line] pairs', type=FileLine.from_str, nargs="*")

    return common_file_line

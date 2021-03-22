import argparse
from common.argparse import FileLine

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
        'pairs', help='One or more [file]s or [file,line] pairs', type=FileLine.from_str, nargs="?")

    return common_file_line

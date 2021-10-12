import argparse
from common import ui_tools
from common import utils
from L1.lower.fileline import FileLine
from common.docker import Docker

def common_pattern_parser_partial():
    common_pattern = argparse.ArgumentParser(add_help=False)
    common_pattern.add_argument(
        'pattern', help='The pattern to test', default=None, nargs='*')
    common_pattern.add_argument('-i', '--case-insensitive', dest='case_sensitive',
                                help='Case sevsitive search (insensitive by default)', action='store_false', default=True)
    common_pattern.add_argument('-@', '--wildness', help='Use incrementally wilder search (1=surround by wildcards. 2=convention variations)',
                                action='count', default=0)
    return common_pattern


def namespace_get(ns, *args, **kwargs):
    return vars(ns).get(*args, **kwargs)

def post_process_excludes(namespace):
    # XXX: unfortunately, there is no such concept of entangled args,
    #      so in order to make --gofignore & --exclude-files function with all combinations,
    #      we shall resort to post processing the namespace instead of using Action on the arg level,
    #      since the desired behavior is on a multi-arg level.
    files = namespace_get(namespace, 'exclude_files', []) or []
    path = namespace_get(namespace, 'gofignore', []) or []
    gofs = utils.get_ignore_list(path)
    namespace.exclude_files = files + gofs

def common_pattern_parser():
    ''' Common flags for cmds with a pattern '''
    common_pattern = common_pattern_parser_partial()
    common_pattern.add_argument(
        '-f', '--files', help='Limit the operation to specific files / directories', type=Docker().outside_to_inside, nargs='+', default=[])
    common_pattern.add_argument(
        '-v', '--invert', action='store_true', help='invert match (like grep -v)')
    common_pattern.add_argument(
        '-w', '--whole-word', help='grep for whole word', action='store_true', default=False)

    # note: see post_process_excludes
    common_pattern.add_argument('--gofignore', help='path to a non-default gofignore', type=Docker().outside_to_inside, default=None)
    common_pattern.add_argument('--exclude-files', nargs='*', type=str, default=None)

    return common_pattern

def common_file_line_parser():
    common_file_line = argparse.ArgumentParser(add_help=False)
    common_file_line.add_argument(
        'pairs', help='One or more [file]s or [file,line] pairs', type=FileLine.from_str, nargs="*")

    return common_file_line

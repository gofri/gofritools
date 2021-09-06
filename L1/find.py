#!/usr/bin/python3
# encoding: utf-8

from common import utils, ui_tools, logging
from L1.lower.iprogram import IProgram
from common.res import SearchRes
from L1.lower.argparse import common_pattern_parser


class Find(IProgram):
    def _run_prog(self, pattern, wildness=0, suffix=None, case_sensitive=True, extra_flags=None, files=None, gof_ignore=None, whole_word=None, invert=False):
        # TODO native invert & whole_word
        # TODO more generally, find should behave like grep, by means that:
        #   * search, rather than match (see note below).
        #   * search is done on the basename, excluding the suffix.
        #   * a first level of wild-ening is searching for any directive of the path
        #     TIP: find -regex (acts on whole path) with '/pattern' should work for searching any-directive of the path
        #   * a whole-word is, by nature, the entire base name.
        #     "by nature", rather than by definition: if the directive is e.g. wierd-file+name.txt,
        #     then whole word will not work properly here, since e.g. 'wierd' is a valid whole-word here.
        #   * THE REAL FIND (this function) should be heavily adjusted accordingly. 
        pattern = [utils.get_wild_version(p, wildness) for p in pattern]
        pattern = [self.__with_regex_prefix(p) for p in pattern]
        SUPRESS_PERM_ERRORS = ['-not', '-readable', '-prune', '-o']
        if suffix:
            suffix = '\(\.\(' + '\|'.join(suffix) + '\)\)$'
            pattern = [p + suffix for p in pattern]
        regextype = ['-regextype', 'grep']
        files_to_search = self.__get_files_to_search(files)
        # https://stackoverflow.com/questions/762348/how-can-i-exclude-all-permission-denied-messages-from-find/25234419#comment48051875_25234419
        print_action = ['-print']

        case_fix = '' if case_sensitive else 'i'
        regex = f'-{case_fix}regex'
        invert = '!' if invert else ''

        # find's -or options take only the first option -- build it with regex instead.
        pattern = [invert, regex, '\|'.join(f'\({p}\)' for p in pattern)]

        # make sure to filter out by suffix even on invertion
        if invert:
            pattern += ['-and', regex, '.*'+suffix]

        cmd = ['find'] + \
            files_to_search + \
            SUPRESS_PERM_ERRORS + \
            regextype + \
            (extra_flags or []) + \
            pattern + \
            print_action

        res = self.ishell.run_cmd(cmd, must_work=True)
        matches = res['stdout'].splitlines()
        ''' TODO integrate into search res record creation '''

        matches = self.__remove_leading_cur_dir(matches)
        matches = utils.unify_paths(matches)

        res = SearchRes.from_list([{'path':match} for match in matches])

        return res

    def __get_files_to_search(self, files):
        return files if files else ['.']

    def __with_regex_prefix(self, pattern):
        return r'\(.*/\|^\)' + pattern  # Regex is fullpath based

    def __remove_leading_cur_dir(self, paths):
        return [path[2:] if path.startswith('./') else path for path in paths]


    @classmethod
    def arg_parser(cls, parent):
        find_parser = cls._add_command_parser(parent, 'find', aliases='f', parents=[
                                            common_pattern_parser()], help='find operations')
        suffix_options = find_parser.add_mutually_exclusive_group()
        suffix_options.add_argument('-s', '--suffix', nargs='*', type=str, help='File extension (e.g. cpp, py)', default=[
                                    'py', 'c', 'cpp', 'cc', 'h', 'hpp', 'java', 'md', 'jinja', 'jinja2', 'json', 'rpm', 'sh', 'text', 'txt', 'go', 'js'])
        # TODO add invert-search for file extension (exclusive group with suffix):
        #   * combinations: (of --invert, --suffix, --invert-suffix)
        #   1. pattern without --invert [regular search]
        #       a. empty --suffix: pattern without suffix
        #       b. non-empty --suffix: pattern with suffix
        #       c. non-empty --invert-suffix: pattern with any suffix, filter-out by suffix
        #   2. pattern with --invert: [invert search]
        #       a. empty --suffix: -not pattern without suffix (no need to re-filter-in suffix)
        #       b. non-empty --suffix: -not pattern with suffix (re-filter-in suffix)
        #       c. non-empty --invert-suffix: -not pattern with any suffix, filter-out by suffix
        # TODO also need to add the suffix support to the new py-native virt version
        suffix_options.add_argument(
            '-S', '--no-suffix', action='store_false', dest='suffix', help='No file extension')

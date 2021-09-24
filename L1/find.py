#!/usr/bin/python3
# encoding: utf-8

from common import utils, ui_tools, logging, docker
from L1.lower.iprogram import IProgram
from L1.lower.results.search_result import SearchResult
from L1.lower.argparse import common_pattern_parser
import itertools


def join_suffix(suffix):
    if suffix:
        return '(\.(' + '|'.join(suffix) + '))$'
    else:
        return '$'

class Find(IProgram):
    '''
    Rules:
    A match is a combination (AND) of two sub-comparisons:
    pattern.search(basename) act like grep on base name.
    suffix.match(extension) act like grep-match on extension=suffix.
    note: where pattern is an or of all actual patterns in the 'pattern' list

    wildness: # reimplement wildness...
    wild=1: match if any(apply pattern to each path directive i.e. dirs/basename).
    wild=2: loose word-separators treatment.

    invertion:
    --invert: invert pattern search (no effect on suffix)
    --invert-suffix: invert suffix search (no effect on pattern)
    One can use whatever combination one would like.

    whole_word:
    Apply whole-word to the pattern.
    '''
    NOT = '-not'
    OR = '-or'
    AND = '-a' # -and is not POSIX compliant; two-consecutive expressions imply -and.
    SUPRESS_PERM_ERRORS = [NOT, '-readable', '-prune', '-o']
    REGEX_TYPE = ['-regextype', 'egrep']
    PRINT_ACTION = ['-print']
    REGEX_START = '^(\./)?'
    def _run_prog(self, pattern, wildness=0, suffix=None, case_sensitive=True, extra_flags=None, files=None, gof_ignore=None, whole_word=None, invert=False, invert_suffix=False, exclude_files=None):
        case_fix = '' if case_sensitive else 'i'
        regex = f'-{case_fix}regex'
        invert = [self.NOT] if invert else []
        invert_suffix = [self.NOT] if invert_suffix else []
        files_to_search = self.__get_files_to_search(files)
        exclude_files = exclude_files or []

        matches = self.get_expressions(regex, pattern, suffix, invert, invert_suffix, wildness, whole_word)

        exclude_files_op = '-regex'
        exclude_files = [ [exclude_files_op, f] for f in exclude_files ]
        excludes = self.get_excludes(exclude_files)
        if excludes:
            matches = excludes + [self.AND] + matches

        cmd = ['find'] + \
            files_to_search + \
            self.SUPRESS_PERM_ERRORS + \
            self.REGEX_TYPE + \
            (extra_flags or []) + \
            matches + \
            self.PRINT_ACTION

        res = self.ishell.run_cmd(cmd, must_work=True)
        matches = utils.safe_splitlines(res['stdout'])

        ''' TODO integrate into search res record creation '''
        matches = self.__remove_leading_cur_dir(matches)
        matches = utils.unify_paths(matches)
        matches = self.__fix_docker_paths(matches)

        res = SearchResult.from_dicts([{'path':match} for match in matches])

        return res

    def __get_files_to_search(self, files):
        # XXX: https://stackoverflow.com/questions/762348/how-can-i-exclude-all-permission-denied-messages-from-find/25234419#comment48051875_25234419
        return files if files else ['.']

    def __with_regex_prefix(self, pattern):
        return r'(.*/|^)' + pattern  # Regex is fullpath based

    def __remove_leading_cur_dir(self, paths):
        return [path[2:] if path.startswith('./') else path for path in paths]

    def __fix_docker_paths(self, paths):
        fixer = docker.Docker().inside_to_outside
        return [fixer(p) for p in paths]

    @classmethod
    def get_expressions(cls, regex, pattern, suffix, invert, invert_suffix, wildness, whole_word):
        '''
            Algorithm rules:
            pattern dir:
                match '{ANY_DIR}[^/*]{pattern}[^/*]/.*$'

            suffix:
                match '^.*\.{suffix}$'

                pattern basename:
                   match '{ANY_DIR}[^/*]{pattern}{ANY_EXT}'

            no-suffix:
                not match '.*/{ANY_EXT}'

                pattern basename:
                   match '{ANY_DIR}[^/*]{pattern}[^/\.]*$'

            always should do:
                pat = pat_basename
                if wild:
                    pat = pat_basename | pat_dir
                find -regex pat and -regex suffix

        '''
        WILDCHAR_IN_DIR = '[^/]*' # assume: after '/'
        ANY_EXT = f'{WILDCHAR_IN_DIR}\.{WILDCHAR_IN_DIR}$' # assume: after /
        ANY_DIR = '^(.*/)?' # assume: leading

        if not pattern:
            pattern = [WILDCHAR_IN_DIR] # look for anything by default

        # whole-word
        if whole_word:
            pattern = [fr'\b{p}\b' for p in pattern]

        # translate each pattern/suffix to its matching list-of-args
        new_suffix = []
        new_pattern = []
        if suffix:
            new_suffix = [ [regex, f'^.*\.{s}$'] for s in suffix ]
            new_pattern = [ [regex, f'{ANY_DIR}{WILDCHAR_IN_DIR}{p}{ANY_EXT}'] for p in pattern ]
        else:
            new_suffix = [ [cls.NOT, regex, f'.*/{ANY_EXT}'] ]
            new_pattern = [ [regex, f'{ANY_DIR}{WILDCHAR_IN_DIR}{p}[^/\.]*$'] for p in pattern ]


        if wildness >= 1: # search all dirs
            pre = f'{ANY_DIR}{WILDCHAR_IN_DIR}'
            post = f'{WILDCHAR_IN_DIR}/.*$'
            new_pattern = [ ['('] + p + [cls.OR, regex, f'{pre}{p}{post}', ')'] \
                            for p in new_pattern ]

        # translate to a concrete line that combines all relations:
        pattern = cls.join_by_or(new_pattern)
        suffix = cls.join_by_or(new_suffix)
        matches = ['('] + invert + pattern + [cls.AND] + invert_suffix + suffix + [')']

        return matches

    @classmethod
    def join_by_or(cls, patterns):
        if not patterns:
            return []
        joiner = lambda i,s: s + ([] if i == len(patterns)-1 else ['-or'])
        patterns = [joiner(i,s) for i, s in enumerate(patterns)]
        return ['('] + list(itertools.chain(*patterns)) + [')']

    @classmethod
    def get_excludes(cls, exclude_files):
        if not exclude_files:
            return []
        exclude_files = cls.join_by_or(exclude_files)
        return [cls.NOT] + exclude_files
        

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
        suffix_options.add_argument(
            '-S', '--no-suffix', action='store_false', dest='suffix', help='No file extension')
        invert_suffix_options = find_parser.add_mutually_exclusive_group()
        invert_suffix_options.add_argument(
            '--invert-suffix', action='store_true', dest='invert_suffix', help='invert search suffix')
        invert_suffix_options.add_argument(
            '--no-invert-suffix', action='store_false', dest='invert_suffix', help='invert search suffix')

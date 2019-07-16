#!/usr/bin/python3
# encoding: utf-8

from common import utils, ui_tools, logging
from L1.iprogram import IProgram
from common.res import SearchRes


class Find(IProgram):
    def _run_prog(self, pattern, wildness=0, suffix=None, case_sensitive=True, extra_flags=None, files=None, gof_ignore=None):
        pattern = [utils.get_wild_version(p, wildness) for p in pattern]
        pattern = [self.__with_regex_prefix(p) for p in pattern]
        SUPRESS_PERM_ERRORS = ['!', '-readable', '-prune', '-o']
        if suffix:
            suffix = '\(\.\(' + '\|'.join(suffix) + '\)\)$'
            pattern = [p + suffix for p in pattern]
        regextype = ['-regextype', 'grep']
        files_to_search = self.__get_files_to_search(files)
        # https://stackoverflow.com/questions/762348/how-can-i-exclude-all-permission-denied-messages-from-find/25234419#comment48051875_25234419
        print_action = ['-print']

        case_fix = '' if case_sensitive else 'i'
        regex = f'-{case_fix}regex'

        # find's -or options take only the first option -- build it with regex instead.
        pattern = [regex, '\|'.join(f'\({p}\)' for p in pattern)]

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

        res = SearchRes([SearchRes.Record(path=match) for match in matches])
        return res

    def __get_files_to_search(self, files):
        return files if files else ['.']

    def __with_regex_prefix(self, pattern):
        return r'\(.*/\|^\)' + pattern  # Regex is fullpath based

    def __remove_leading_cur_dir(self, paths):
        return [path[2:] if path.startswith('./') else path for path in paths]

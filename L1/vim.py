#!/usr/bin/python3
# encoding: utf-8
from common import utils, logging
from L1.lower.iprogram import IProgram
import argparse
from L1.lower.argparse import common_file_line_parser, FileLine

class Vim(IProgram):
    def _run_prog(self, pairs, view_mode, readonly, reverse):
        assert len(pairs) > 0, "empty file selection for vim"
        self.__open_multiple_files(pairs, view_mode, readonly, reverse)

    def is_reverse(self, reverse, readonly):
        if reverse in (True, False):
            return reverse
        else: # if not explicitly set, let readonly dictate it: prefer reversed order if the files are modifiable
            return not readonly

    def __open_multiple_files(self, pairs, view_mode, readonly, reverse):
        logging.verbose_print(f'read/reverse: {readonly}, {reverse}, {self.is_reverse(reverse, readonly)}')
        files = [p.file for p in pairs]
        do_reverse = self.is_reverse(reverse, readonly)
        if readonly:
            vim_cmd = ['vim', '-R']
        else:
            vim_cmd = ['vim']
        with utils.MultipleFiles(files):
            if view_mode in ('c', 'combo'):
                if do_reverse:
                    pairs = list(reversed(pairs))
                # XXX: The first arg file is passed differently (w/o vsp & as distinct args for file nad line).
                last = pairs[-1]
                last_line = self.__fix_default_line(last.line)
                last_file_args = [f'+{last_line}', last.file]

                # XXX: In this split mode, vim expects the file in a reversed oreder
                rest_files_args = [f'+vsp +{self.__fix_default_line(p.line)} {p.file}' for p in reversed(pairs[:-1])]

                args = last_file_args + rest_files_args
                self.ishell.interactive_cmd(vim_cmd + args)

            elif view_mode in ('s', 'series'):
                pairs = FileLine.as_safe_list(pairs, sorted_=do_reverse)
                for p in pairs:
                    if len(pairs) > 1: # make default=series hidden when n_files=1
                        print(
                            f'Showing {p} | Press enter to continue, s/stop to stop')
                        if input() in ('s', 'stop'):
                            break
                    args = [p.file, f'+{self.__fix_default_line(p.line)}']
                    self.ishell.interactive_cmd(vim_cmd + args)

    def __fix_default_line(self, line):
        return line or '0'

    @classmethod
    def arg_parser(cls, parent):
        vim_parser = cls._add_command_parser(parent, 
            'vim', aliases=['v'], parents=[common_file_line_parser()], help='Open file in vim')
        vim_parser.add_argument('-v', '--view-mode', help='Choose view mode',
                                choices=['c', 'combo', 's', 'series'], default='series')
        vim_parser.add_argument('-r', '--reverse', action='store_true', help='show in reverse order',
                                dest='reverse', default=None)
        vim_parser.add_argument('-R', '--no-reverse', action='store_false', help='show in original order',
                                dest='reverse', default=None)
        vim_parser.add_argument('-O', '--readonly', action='store_true', help='open vim in readonly mode',
                                default=None)

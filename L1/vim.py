#!/usr/bin/python3
# encoding: utf-8
from common import utils
from L1.iprogram import IProgram
import argparse
from L1.common.argparse import common_file_line_parser

class Vim(IProgram):
    def _run_prog(self, pairs, view_mode):
        assert len(pairs) > 0, "empty file selection for vim"
        self.__open_multiple_files(pairs, view_mode)

    def __open_multiple_files(self, pairs, view_mode):
        files = [p.file for p in pairs]
        with utils.MultipleFiles(files):
            if view_mode in ('c', 'combo'):
                # XXX: The first arg file is passed differently (w/o vsp & as distinct args for file nad line).
                last = pairs[-1]
                last_line = self.__fix_default_line(last.line)
                last_file_args = [f'+{last_line}', last.file]

                # XXX: In this split mode, vim expects the file in a reversed oreder
                rest_files_args = [f'+vsp +{self.__fix_default_line(p.line)} {p.file}' for p in reversed(pairs[:-1])]

                args = last_file_args + rest_files_args
                self.ishell.interactive_cmd(['vim'] + args)

            elif view_mode in ('s', 'series'):
                for p in pairs:
                    print(
                        f'Showing {p} | Press enter to continue, s/stop to stop')
                    if input() in ('s', 'stop'):
                        break
                    args = [p.file, f'+{self.__fix_default_line(p.line)}']
                    self.ishell.interactive_cmd(['vim'] + args)

    def __fix_default_line(self, line):
        return line or '0'

    @classmethod
    def arg_parser(cls, parent):
        vim_parser = cls._add_command_parser(parent, 
            'vim', aliases=['v'], parents=[common_file_line_parser()], help='Open file in vim')
        vim_parser.add_argument('-v', '--view-mode', help='Choose view mode',
                                choices=['c', 'combo', 's', 'series'], default='combo')

#!/usr/bin/python3
# encoding: utf-8
from common import utils
from L1.iprogram import IProgram
import argparse
from L1.common.argparse import common_file_line_parser


# TODO complete code duplicate with vim
class Less(IProgram):
    def _run_prog(self, pairs):
        assert len(pairs) > 0, "empty file selection for less"
        self.__open_multiple_files(pairs)

    def __open_multiple_files(self, pairs):
        files = [p.file for p in pairs]
        with utils.MultipleFiles(files):
            for p in pairs:
                print(
                    f'Showing {p} | Press enter to continue, s/stop to stop')
                if input() in ('s', 'stop'):
                    break
                args = [f'+{self.__fix_default_line(p.line)}', p.file]
                self.ishell.interactive_cmd(['less'] + args)

    def __fix_default_line(self, line):
        return line or '0'

    @classmethod
    def arg_parser(cls, parent):
        less_parser = cls._add_command_parser(parent, 
            'less', aliases=['l'], parents=[common_file_line_parser()], help='Open file in less')

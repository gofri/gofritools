#!/usr/bin/python3
# encoding: utf-8

from L1.iprogram import IProgram
from common.stringification import Stringification
from common import logging


class Copy(IProgram):
    def _run_prog(self, text, xargs, selection):
        if xargs:
            text = text.replace('\n', ' ')
        self.ishell.run_cmd(['xclip', '-selection', selection],
                            stdin=text, must_work=True, fetch_output=False)
        logging.verbose_print('Copied.')

    @classmethod
    def arg_parser(cls, parent):
        copy_parser = cls._add_command_parser(parent, 
            'copy', aliases=['c'], parents=[], help='Copy the output')
        copy_parser.add_argument('-s', '--selection', help='copy type',
                                 default='clip-board', choices=['primary', 'secondary', 'clip-board'])
        copy_parser.add_argument('-t', '--text', help='text to copy', default='')
        copy_parser.add_argument('-x', '--xargs', help='xargs (replace line-break with space)', action='store_true', default=False)

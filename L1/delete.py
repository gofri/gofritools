#!/usr/bin/python3
# encoding: utf-8
from common import utils, logging
from L1.common.argparse import FileLine
from L1.common.iprogram import IProgram
from L1.common.argparse import common_file_line_parser

class Delete(IProgram):
    def _run_prog(self, pairs):
        pairs = FileLine.as_safe_list(pairs)
        for p in pairs:
            logging.verbose_print(f'Deleting: {p}')
            self.ishell.run_cmd(['sed', '-i'] + [f'{p.line}d'] + ['--', p.file])

    @classmethod
    def arg_parser(cls, parent):
        delete_parser = cls._add_command_parser(parent, 
            'delete', aliases=['d'], parents=[common_file_line_parser()], help='delete the line (sed-based)')

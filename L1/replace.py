#!/usr/bin/python3
# encoding: utf-8
from common import utils
from L1.lower.iprogram import IProgram
from L1.lower.argparse import FileLine
from L1.lower.argparse import common_file_line_parser


class Replace(IProgram):
    def _run_prog(self, before, after, pairs, global_replace):
        g = 'g' if global_replace else ''
        before, after = map(self.escape, (before, after))
        pairs = FileLine.as_safe_list(pairs)
        for p in pairs:
            self.ishell.run_cmd(
                ['sed', '-i'] + [f'{p.line}s/{before}/{after}/{g}'] + ['--', p.file])

    def escape(self, s): 
        return s.replace('/', '\/')

    @classmethod
    def arg_parser(cls, parent):
        replace_parser = cls._add_command_parser(parent, 'replace', aliases=['r'], parents=[common_file_line_parser()],
            help='replace text with other text (sed-based)')
        replace_parser.add_argument('before', help='pattern to search', type=str)
        replace_parser.add_argument(
            'after', help='pattern to set isntead', type=str)
        replace_parser.add_argument('-G', '--no-global-replace', dest='global_replace', default=True,
                                    help='disable global replace (enabled by default)', action='store_false')


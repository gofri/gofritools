#!/usr/bin/python3
# encoding: utf-8
from common import utils, logging
from common.argparse import FileLine
from L1.iprogram import IProgram

class Delete(IProgram):
    def _run_prog(self, pairs):
        pairs = FileLine.as_safe_list(pairs)
        for p in pairs:
            logging.verbose_print(f'Deleting: {p}')
            self.ishell.run_cmd(['sed', '-i'] + [f'{p.line}d'] + ['--', p.file])

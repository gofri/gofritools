#!/usr/bin/python3
# encoding: utf-8
from common import utils
from L1.iprogram import IProgram
from common.argparse import FileLine


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

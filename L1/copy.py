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

#!/usr/bin/python3
# encoding: utf-8
from L1.lower.iprogram import IProgram
from common import logging


class Trim(IProgram):

    def _run_prog(self, search_res):
        search_res.trim()
        logging.verbose_print('Trimed raw text (colored text does not trim).')
        return search_res

    @classmethod
    def arg_parser(cls, parent):
        trim_parser = cls._add_command_parser(parent, 
            'trim', aliases='t', parents=[], help='Trim text (strip)')

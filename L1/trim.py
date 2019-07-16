#!/usr/bin/python3
# encoding: utf-8
from L1.iprogram import IProgram
from common import logging


class Trim(IProgram):

    def _run_prog(self, search_res):
        search_res.trim()
        logging.verbose_print('Trimed raw text (colored text does not trim).')
        return search_res

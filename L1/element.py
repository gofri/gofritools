#!/usr/bin/python3
# encoding: utf-8

from L1.iprogram import IProgram


class Element(IProgram):
    def _run_prog(self, data, elements, sort=False, unify=False, do_choice=True, trim_on_sort=True):
        data.keep_only(elements, sort, unify, do_choice, trim_on_sort=True)
        return data

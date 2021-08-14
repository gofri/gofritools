#!/usr/bin/python3
# encoding: utf-8

from L1.lower.iprogram import IProgram


class Element(IProgram):
    def _run_prog(self, data, elements, sort=False, unify=False, do_choice=True, trim_on_sort=True):
        data.keep_only(elements, sort, unify, do_choice, trim_on_sort=True)
        return data

    @classmethod
    def arg_parser(cls, parent):
        element_parser = cls._add_command_parser(parent, 'element', aliases=['e'], parents=[
        ], help='Select one or more element from previous output (path/line/text/text_colored)')
        element_parser.add_argument('elements', help='element', nargs='*')
        element_parser.add_argument(
            '-s', '--sort', help='Sort by (instead of choose) the element.', action='store_true')
        element_parser.add_argument(
            '-u', '--unify', help='Unify the results based on a single element', action='store_true')
        element_parser.add_argument('-n', '--no-choice', dest='do_choice', default=True,
                                    help='Prevent choosing the element (for e.g. unify)', action='store_false')
        element_parser.add_argument('-T', '--no-trim-on-sort', dest='trim_on_sort', default=True,
                                    help='Prevent trim before sorting (trimming only for sort - does not effect search res)', action='store_false')


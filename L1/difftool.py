#!/usr/bin/python3
# encoding: utf-8
from common import utils
from L1.lower.iprogram import IProgram


class Difftool(IProgram):
    def _run_prog(self, files, tool):
        assert len(files) > 0, "empty file selection for difftool"
        self.__open_multiple_files(files, tool)

    def __open_multiple_files(self, files, tool):
        with utils.MultipleFiles(files):
            self.ishell.interactive_cmd([tool] + files)

    @classmethod
    def arg_parser(cls, parent):
        difftool_parser = cls._add_command_parser(parent, 
            'difftool', aliases=['dt'], parents=[], help='Open file in difftool')
        difftool_parser.add_argument(
            'files', help='One or more files', type=str, nargs="*", default=[])
        difftool_parser.add_argument(
            '--tool', help='Choose tool to use', type=str, default='meld')

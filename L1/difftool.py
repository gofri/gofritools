#!/usr/bin/python3
# encoding: utf-8
from common import utils
from L1.iprogram import IProgram


class Difftool(IProgram):
    def _run_prog(self, files, tool):
        assert len(files) > 0, "empty file selection for difftool"
        self.__open_multiple_files(files, tool)

    def __open_multiple_files(self, files, tool):
        with utils.MultipleFiles(files):
            self.ishell.interactive_cmd([tool] + files)

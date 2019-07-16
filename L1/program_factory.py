#!//bin/python3
# encoding: utf-8
from L1.grep import Grep
from L1.find import Find
from L1.vim import Vim
from L1.copy import Copy
from L1.select import Select
from L1.element import Element
from L1.difftool import Difftool
from common.logging import verbose_print
from common.ifactory import IFactory
from L0.shell_factory import ShellFactory


class ProgramFactory(IFactory):
    PROGRAMS = {
        'grep': Grep,
        'find': Find,
        'vim': Vim,
        'copy': Copy,
        'select': Select,
        'element': Element,
        'difftool': Difftool,
    }

    def __init__(self, shell_name=None):
        self.shell = ShellFactory().create(shell_name)

    def create(self, command):
        prog_type = self.get_prog(command)
        return prog_type(self.shell)

    @classmethod
    def get_prog(cls, name):
        return cls.PROGRAMS[name]

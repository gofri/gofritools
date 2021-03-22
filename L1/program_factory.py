#!//bin/python3
# encoding: utf-8
from common.logging import verbose_print
from common.ifactory import IFactory
from L0.shell_factory import ShellFactory

from L1.grep import Grep
from L1.find import Find
from L1.vim import Vim
from L1.less import Less
from L1.copy import Copy
from L1.delete import Delete
from L1.replace import Replace
from L1.select import Select
from L1.element import Element
from L1.difftool import Difftool
from L1.trim import Trim

class ProgramFactory(IFactory):
    PROGRAMS = {
        'grep': Grep,
        'find': Find,
        'vim': Vim,
        'less': Less,
        'copy': Copy,
        'delete': Delete,
        'replace': Replace,
        'select': Select,
        'element': Element,
        'difftool': Difftool,
        'trim': Trim,
    }

    def __init__(self, shell_name=None):
        self.shell = ShellFactory().create(shell_name)

    def create(self, command):
        prog_type = self.get_prog(command)
        return prog_type(self.shell)

    @classmethod
    def get_prog(cls, name):
        return cls.PROGRAMS[name]

    @classmethod
    def arg_parser(cls, parent):
        for name, prog in cls.PROGRAMS.items():
            prog.arg_parser(parent)

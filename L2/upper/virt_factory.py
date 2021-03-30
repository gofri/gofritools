#!/usr/bin/python3
# encoding: utf-8
from L2.virt_grep import VirtGrep
from L2.virt_find import VirtFind
from L2.virt_vim import VirtVim
from L2.virt_less import VirtLess
from L2.virt_replace import VirtReplace
from L2.virt_delete import VirtDelete
from L2.virt_copy import VirtCopy
from L2.virt_select import VirtSelect
from L2.virt_trim import VirtTrim
from L1.upper.program_factory import ProgramFactory
from L2.virt_element import VirtElement
from L2.virt_difftool import VirtDifftool


class VirtFactory(ProgramFactory):
    VIRT_PROGRAMS = {
        'grep': VirtGrep,
        'find': VirtFind,
        'vim': VirtVim,
        'less': VirtLess,
        'replace': VirtReplace,
        'delete': VirtDelete,
        'copy': VirtCopy,
        'select': VirtSelect,
        'trim': VirtTrim,
        'element': VirtElement,
        'difftool': VirtDifftool,
    }

    def __init__(self, prev_output, shell_name=None):
        ProgramFactory.__init__(self, shell_name)
        self.prev_output = prev_output

    def create(self, command):
        if self.prev_output:  # and not self.virt_set: # Revert to regular program factory if no input
            virt_prog_type = self.get_virt_prog_type(command)
            return virt_prog_type(self.shell, self.prev_output)
        else:
            return ProgramFactory.create(self, command)

    @classmethod
    def get_virt_prog_type(cls, name):
        return cls.VIRT_PROGRAMS[name]

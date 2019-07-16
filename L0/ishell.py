#!/usr/bin/python3
# encoding: utf-8

from abc import ABC, abstractmethod


class IShell(ABC):
    @abstractmethod
    def run_cmd(self, cmd: list, expect_output=None, stdin='', must_work=True, **kwargs):
        pass

    @abstractmethod
    def interactive_cmd(self, cmd, must_work=True):
        pass

    @abstractmethod
    def run_on_shell(self, cmd_str, must_work=True):
        pass

    POSIX_SUCCESS = 0
    INTERNAL_ERROR_RES = -666

    @classmethod
    def internal_error(cls):
        return cls.build_res(cls.INTERNAL_ERROR_RES, '', 'Internal Error')

    @classmethod
    def empty_res(cls, rc=INTERNAL_ERROR_RES):
        return cls.build_res(rc, '', 'Empty Result')

    @classmethod
    def build_res(cls, rc=POSIX_SUCCESS, stdout='', stderr=''):
        return {
            'stdout': stdout,
            'stderr': stderr,
            'rc': rc,
        }

    @classmethod
    def is_internal_error(cls, res):
        return res['rc'] == cls.INTERNAL_ERROR_RES

    class CmdFailureException(Exception):
        def __init__(self, res, cwd, *args, **kwargs):
            super().__init__(res, *args, **kwargs)
            self.res = res
            self.cwd = cwd

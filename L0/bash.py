#!/usr/bin/python3
# encoding: utf-8

import subprocess
from common import logging
from L0.ishell import IShell


class Bash(IShell):
    def run_cmd(self, cmd, expect_output=None, stdin='', must_work=True, stdout_enough=False, fetch_output=True, **kwargs):
        ''' TODO: fetch_output=False is probably broken '''
        ''' TODO: expect_output|must_work|stdout_enough -- put into enum or something'''
        cmd = [x for x in cmd if x.strip()]
        logging.verbose_print_cmd(cmd, 'running cmd:')

        output_pipe = subprocess.PIPE if fetch_output else None
        p = subprocess.Popen(cmd, stdout=output_pipe, stderr=output_pipe,
                             stdin=subprocess.PIPE, encoding='utf-8', **kwargs)
        stdout, stderr = p.communicate(stdin)

        res = IShell.build_res(p.returncode, stdout, stderr)

        if res['rc'] != self.POSIX_SUCCESS:
            msg = 'command execution failed:\n{}'.format(res)
            if stdout_enough and res['stdout']:
                logging.verbose_print(f'Command partially failed: {stderr}')
                return res
            if must_work:
                raise IShell.CmdFailureException(
                    res, cmd, kwargs.get('cwd', None))
            else:
                logging.verbose_print(msg)
        elif expect_output:
            assert expect_output == stdout, 'Expected output:\n{}\n\nGot:\n{}'.format(
                expect_output, stdout)

        return res

    def get_output(self, cmd: list, /, *args, strip=False, **kwargs):
        output = self.run_cmd(cmd, must_work=True)['stdout']
        if strip:
            output = output.strip()
        return output

    def interactive_cmd(self, cmd, must_work=False):
        logging.verbose_print_cmd(cmd, 'running interactive cmd:')
        with open('/dev/tty', 'r') as tty_stdin:
            res = subprocess.call(cmd, stdin=tty_stdin)
        if must_work and res != self.POSIX_SUCCESS:
            raise IShell.CmdFailureException(res)

    def run_on_shell(self, cmd_str, must_work=True):
        logging.verbose_print(f'running shell cmd: {cmd_str}')
        res = subprocess.call(cmd_str, encoding='utf8', shell=True)
        if must_work and res != self.POSIX_SUCCESS:
            raise IShell.CmdFailureException(res)

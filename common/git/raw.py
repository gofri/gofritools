from common.git.exceptions import *
from common import logging


class RawGitCommands(object):
    ''' Helper class for git operations. '''

    GIT_HEAD = 'HEAD'

    def __init__(self, ishell, path=None):
        self.ishell = ishell
        # XXX: self.path is yet unset, so we must provide a path
        self.path = self.get_base_dir(path or '.')

    def __get_single_output(self, cmd, cwd=None):
        cwd = cwd or self.path
        return self.ishell.get_output(cmd, cwd=cwd, strip=True)

    def __get_multi_output(self, cmd, cwd=None):
        res = self.__get_single_output(cmd, cwd).split('\n')
        return [x.strip() for x in res if x.strip()]

    def get_base_dir(self, cwd=None):
        cmd = ['git', 'rev-parse', '--show-toplevel']
        cwd = cwd or self.path
        try:
            return self.__get_single_output(cmd, cwd)
        except Exception as e:
            logging.print_to_stderr(f'Failed to find git repo: {e}')
            raise NonGit(self.path, e)

    def get_remote(self):
        cmd = ['git', 'remote', 'get-url', 'origin']
        return self.__get_single_output(cmd)

    def get_current_branch(self):
        cmd = ['git', 'branch', '--show-current']
        return self.__get_single_output(cmd)

    def get_current_tags(self):
        return self.get_pointing_tags(self.GIT_HEAD)

    def get_current_hash(self):
        cmd = ['git', 'rev-parse', self.GIT_HEAD]
        return self.__get_single_output(cmd)

    def get_pointing_branches(self, commit):
        cmd = ['git', 'branch', '--points-at', commit]
        ret = self.__get_multi_output(cmd)
        return self._parse_branches(ret)

    def get_containing_branches(self, commit):
        cmd = ['git', 'branch', '--contains', commit]
        ret = self.__get_multi_output(cmd)
        return self._parse_branches(ret)

    def _parse_single_branch(self, b):
        ''' Returns a tuple of (branch_name, is_current_branch) '''
        b = b.strip()

        # Strip the current branch indicator
        CURRENT_BNRACH_PREFIX = '* '
        if b.startswith(CURRENT_BNRACH_PREFIX):
            b = b[len(CURRENT_BNRACH_PREFIX):]

            # Strip the HEAD-detached indicator
            HEAD_PREFIX, HEAD_SUFFIX = '(HEAD detached at ', ')'
            if b.startswith(HEAD_PREFIX):
                b = b[len(HEAD_PREFIX):-len(HEAD_SUFFIX)]

        return b

    def _parse_branches(self, org_branches: list):
        return [self._parse_single_branch(b) for b in org_branches if b.strip()]

    def get_pointing_tags(self, commit):
        cmd = ['git', 'tag', '--points-at'] + [commit]
        return self.__get_multi_output(cmd)

    def get_containing_tags(self, commit):
        cmd = ['git', 'tag', '--contains'] + [commit]
        return self.__get_multi_output(cmd)

    def get_user_mail(self):
        USER_MAIL = 'user.email'
        LOCAL = '--local'
        cmd = ['git', 'config', LOCAL, USER_MAIL]
        try:
            return self.__get_single_output(cmd)
        except Exception:
            try:
                cmd.remove(LOCAL)  # No local email, try global
                return self.__get_single_output(cmd)
            except Exception:
                return NotConfigured('Email is not configured')

    def blame(self, file_path):
        SUPRESS_AUTHOR = '-s'
        ADD_ORG_LINE_NUM = '-n'

        cmd = ['git', 'blame', SUPRESS_AUTHOR, ADD_ORG_LINE_NUM, file_path]
        res = self.__get_multi_output(cmd)
        return [self._parse_blame_line(line) for line in res]

    def get_commit_diff(self, commit, colored=False):
        DIFF_SINGLE_COMMIT = '^!'
        COLORED = '--color=always'
        colored = [COLORED] if colored else []
        commit = commit + DIFF_SINGLE_COMMIT
        cmd = ['git', 'diff'] + colored + [commit]
        # return self.__get_multi_output(cmd)
        return self.__get_single_output(cmd)

    def _parse_blame_line(self, line):
        hashval, rest = line.split(' ', 1)
        org_line_no, rest = rest.strip().split(' ', 1)

        rest = rest.strip()
        line_no, rest = rest.split(')', 1)
        text = rest.strip()

        return hashval, org_line_no, line_no, text

from dataclasses import dataclass
from common.utils import SimpleCache
from common.git.exceptions import *
from common.git.raw import RawGitCommands
from builtins import object


class Commit(object):
    ''' A single commit object. '''

    def __init__(self, key: 'CommitKey'):
        self.key = key
        self.git_controller = self.key.repo.git_controller
        self._pointing_branches = SimpleCache(self._do_get_pointing_branches)
        self._containing_branches = SimpleCache(
            self._do_get_containing_branches)
        self._tags = SimpleCache(self._do_get_tags)
        self._names = SimpleCache(self._do_get_names)
        self._diff = SimpleCache(self._do_get_diff)

    def is_repo_head(self):
        return self.key

    @property
    def pointing_branches(self):
        return self._pointing_branches.fetch()

    @property
    def containing_branches(self):
        return self._containing_branches.fetch()

    @property
    def tags(self):
        return self._tags.fetch()

    @property
    def names(self):
        return self._names.fetch()
        ''' Get commit names with the followng order: Current-Branch > Branches > Tags > Hash '''

    @property
    def hash(self):
        return self.key.hash

    def _do_get_names(self):
        names = []

        names += self.pointing_branches
        # TODO also head containing branches as e.g. BRANCH~23
        names += self.tags
        names.append(self.hash)

        return names

    def _do_get_pointing_branches(self):
        return self.git_controller.get_pointing_branches(self.key.hash.full)

    def _do_get_containing_branches(self):
        return self.git_controller.get_containing_branches(self.key.hash.full)

    def _do_get_tags(self):
        return self.git_controller.get_containing_tags(self.key.hash.full)

    def _do_get_diff(self):
        return self.git_controller.get_commit_diff(self.key.hash.full)


class Repo(object):
    ''' A cloned (on-the-filesystem) git repo representation. '''

    def __init__(self, ishell, path):
        self.ishell = ishell
        self.user_path = path
        self.git_controller = RawGitCommands(self.ishell, self.user_path)
        self._base_dir = self.git_controller.path
        self._head = SimpleCache(self._do_get_head)
        self._remote = SimpleCache(self.git_controller.get_remote)
        self._cur_branch = SimpleCache(self.git_controller.get_current_branch)

    @property
    def base_dir(self):
        return self._base_dir.fetch()

    @property
    def head(self):
        return self._head.fetch()

    @property
    def remote(self):
        return self._remote.fetch()

    def _do_get_head(self):
        head_hash = self.git_controller.get_current_hash()
        return CommitKey(self, Hash(head_hash))

    def __eq__(self, other):
        return self.remote == other.remote

    def __str__(self):
        return self.remote

    # TODO get current branch (isn't directly implied by commit)


class Hash(object):
    FULL_LENGTH = 40
    SHORT_LENGTH = 10

    def __init__(self, hashval: str):
        self.hash = hashval

    @property
    def full(self):
        return self.hash

    @property
    def short(self):
        return self.hash[:self.SHORT_LENGTH]

    def __eq__(self, other):
        return self.hash == other.hash

    def __str__(self):
        return self.short

    def __repr__(self):
        return self.short


class Tag(object):
    pass  # TODO


@dataclass
class CommitKey(object):
    ''' UID for commit: repo + commit hash. '''
    repo: Repo
    hash: Hash

    def __str__(self):
        return f'{self.repo}:{self.hash}'


def foo(f):
    from L0.bash import Bash
    r = RawGitCommands(Bash())
    res = r.blame(f or '../../main.py')
    # print('\n'.join([str(s) for s in res]))
    def make_commit(x): return Commit(CommitKey(Repo(Bash(), '.'), Hash(x)))

    master = make_commit('d022ca3')
    with_tags = make_commit('9048921d')
    current = make_commit('e244cff')

    print(master.names)
    print(current.names)

    diff = r.get_commit_diff(with_tags.hash.full, True)
    print(diff)

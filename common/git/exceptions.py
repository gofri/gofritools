class NonGit(Exception):
    def __init__(self, path, *args, **kwargs):
        self.path = path
        self.extra = args, kwargs

    def __str__(self):
        return f'{self.path} is not inside a git repo.'


class NonBranch(Exception):
    def __str__(self):
        return f'Current HEAD is detached (no branch)'


class NotConfigured(Exception):
    pass

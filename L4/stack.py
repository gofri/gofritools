from L4.istack import IStack
from L3.pipe_factory import PipeFactory
from L3.nullpipe import NullPipe
from common.res import SearchRes
from common import utils

class Stack(IStack):
    class OpMessage(Exception): pass

    def __init__(self):
        self.reset()

    @property
    def size(self):
        return len(self.stack)

    @property
    def real_size(self):
        null_pipe_cnt = 1
        return len(self.stack) - null_pipe_cnt

    def cur(self):
        try:
            return self.stack[self.pos]
        except IndexError:
            raise RuntimeError('Cannot call cur on empty stack')

    def put(self, args_ns):
        if args_ns.command == 'stepf':
            self._step_forward()
        elif args_ns.command == 'stepb':
            self._step_back()
        else:
            self._put_one(args_ns)

        return self.cur().output

    def reset(self):
        self.stack = [NullPipe()]
        self.pos = 0

    def _put_one(self, args_ns):
        stdin = self.cur().output
        pipe = PipeFactory(stdin).create()
        _ = pipe.run(args_ns)

        if pipe.stackable:
            self.pos += 1
            self.stack[:] = self.stack[:self.pos]
            self.stack.append(pipe)

        if pipe.dirtying:
            self.refresh()

    def _step_forward(self):
        if self.pos == self.size-1:
            raise self.OpMessage('Nowhere forward to go.')
        elif self.pos >= self.size:
            raise RuntimeError('Unexpected position.')
        self.pos += 1

    def _step_back(self):
        if self.pos > 0:
            self.pos -= 1
        elif self.pos == 0:
            raise self.OpMessage('Nowhere backward to go.')
        else:
            raise RuntimeError('Unexpected underflow.')

    def refresh(self):
        res = SearchRes()
        for p in self.stack:
            res = p.refresh(res)

    def picklize(self):
        return utils.picklize(self)
